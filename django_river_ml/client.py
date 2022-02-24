from river.metrics.base import ClassificationMetric

import django_river_ml.storage as storage
import django_river_ml.exceptions as exceptions
import django_river_ml.utils as utils
import django_river_ml.announce as announce

import json
import copy


class RiverClient:
    """
    A river client includes shared functions for interacting with storage.
    This implementation was chosen so it can easily be plugged into another
    kind of server without needing to deal with the server-specific requests.
    """

    def __init__(self):
        self.db = storage.get_db()

    def stats(self):
        try:
            stats = self.db["stats"]
        except KeyError:
            raise exceptions.InvalidUsage(message="No flavor has been set.")

        return {
            "predict": {
                "n_calls": int(stats["predict_mean"].n),
                "mean_duration": int(stats["predict_mean"].get()),
                "mean_duration_human": utils.humanize_ns(
                    int(stats["predict_mean"].get())
                ),
                "ewm_duration": int(stats["predict_ewm"].get()),
                "ewm_duration_human": utils.humanize_ns(
                    int(stats["predict_ewm"].get())
                ),
            },
            "learn": {
                "n_calls": int(stats["learn_mean"].n),
                "mean_duration": int(stats["learn_mean"].get()),
                "mean_duration_human": utils.humanize_ns(
                    int(stats["learn_mean"].get())
                ),
                "ewm_duration": int(stats["learn_ewm"].get()),
                "ewm_duration_human": utils.humanize_ns(int(stats["learn_ewm"].get())),
            },
        }

    def stream_events(self):
        """
        Stream events from the events announcer.
        """
        messages = announce.EVENTS_ANNOUNCER.listen()
        return self._stream_announcer(self, messages)

    def stream_metrics(self):
        """
        Stream events from the metrics announcer.
        """
        messages = announce.METRICS_ANNOUNCER.listen()
        return self._stream_announcer(self, messages)

    def metrics(self):
        """
        Get metrics from the database
        """
        try:
            metrics = self.db["metrics"]
        except KeyError:
            raise exceptions.FlavorNotSet
        return {metric.__class__.__name__: metric.get() for metric in metrics}

    def add_model(self, model, name=None):
        """
        Add a model by name (e.g., via API post)
        """
        # Validate the model
        try:
            flavor = self.db["flavor"]
        except KeyError:
            raise exceptions.FlavorNotSet

        ok, error = flavor.check_model(model)
        if not ok:
            raise exceptions.InvalidUsage(message=error)
        name = storage.add_model(model, name=name)
        self.db[
            "default_model_name"
        ] = name  # the most recent model becomes the default
        return {"name": name}

    def get_model(self, name):
        """
        Get a model by name
        """
        name = self.db["default_model_name"] if name is None else name
        model = self.db[f"models/{name}"]
        return model

    def delete_model(self, name):
        """
        Delete a model by name.
        """
        key = f"models/{name}"
        if key not in self.db:
            return False
        del self.db[key]
        return True

    def models(self):
        """
        Get models known to a database.
        """
        model_names = sorted(
            [k.split("/", 1)[1] for k in self.db if k.startswith("models/")]
        )
        return {"models": model_names, "default": self.db.get("default_model_name")}

    def _stream_announcer(self, announcer):
        """
        Shared function to stream events from an announcer.
        """
        while True:
            item = announcer.get()  # blocks until a new message arrives
            yield item

    # Learn and predict!

    def learn(
        self,
        ground_truth=None,
        prediction=None,
        features=None,
        model_name=None,
        identifier=None,
    ):
        """
        A learning event takes a learning schema
        """
        # If an ID is given, then retrieve the stored info.
        try:
            memory = self.db["#%s" % identifier] if identifier else {}
        except KeyError:
            raise exceptions.InvalidUsage(
                message=f"No information stored for ID '{identifier}'."
            )

        model_name = memory.get("model", model_name)
        features = memory.get("features", features)
        prediction = memory.get("prediction", prediction)

        # Raise an error if no features are provided
        if features is None:
            raise exceptions.InvalidUsage(
                message="No features are stored and none were provided."
            )

        # Load the model
        if model_name is None:
            try:
                default_model_name = self.db["default_model_name"]
            except KeyError:
                raise exceptions.InvalidUsage(message="No default model has been set.")
            model_name = default_model_name

        try:
            model = self.db[f"models/{model_name}"]
        except KeyError:
            raise exceptions.InvalidUsage(message=f"No model named '{model_name}'.")

        # Obtain a prediction if none was made earlier
        if prediction is None:
            flavor = self.db["flavor"]
            pred_func = getattr(model, flavor.pred_func)
            try:
                prediction = pred_func(x=copy.deepcopy(features))
            except Exception as e:
                raise exceptions.InvalidUsage(message=repr(e))

        metrics = self.update_metrics(prediction, ground_truth)

        # Update the model
        # TODO what if we do not have ground truth?
        try:
            model.learn_one(x=copy.deepcopy(features), y=ground_truth)
        except Exception as e:
            raise exceptions.InvalidUsage(message=repr(e))

        self.db[f"models/{model_name}"] = model
        self.announce_event(
            "learn",
            {
                "model": model_name,
                "features": features,
                "prediction": prediction,
                "ground_truth": ground_truth,
            },
        )
        self.announce_metrics(metrics)

        # Delete the id from the db
        if identifier:
            self.delete_id(identifier)
        return True

    def predict(self, features, model_name=None, identifier=None, model=None):
        """
        Run a prediction
        """
        try:
            default_model_name = self.db["default_model_name"]
        except KeyError:
            raise exceptions.InvalidUsage(message="No default model has been set.")

        model_name = model_name or default_model_name
        try:
            model = self.db[f"models/{model_name}"]
        except KeyError:
            raise exceptions.InvalidUsage(message=f"No model named '{model_name}'.")

        # We make a copy because the model might modify the features in-place while we want to be able
        # to store an identical copy
        features = copy.deepcopy(features)

        # Make the prediction
        flavor = self.db["flavor"]
        pred_func = getattr(model, flavor.pred_func)
        try:
            pred = pred_func(x=features)
        except Exception as e:
            raise exceptions.InvalidUsage(message=repr(e))

        # The unsupervised parts of the model might be updated after a prediction, so we need to store it
        self.db[f"models/{model_name}"] = model

        # Announce the prediction
        self.announce_event(
            "predict",
            {
                "model": model_name,
                "features": features,
                "prediction": pred,
            },
        )

        # If an ID is provided, then we store the features in order to be able to use them for learning
        # further down the line. We remove granularity about creation (200 vs 201) here.
        created = False
        if identifier:
            self.db["#%s" % identifier] = {
                "model": model_name,
                "features": features,
                "prediction": pred,
            }
            created = True
        return {"model": model_name, "prediction": pred, "created": created}

    def announce_metrics(self, metrics):
        """
        Announce the current metric values
        """
        if announce.METRICS_ANNOUNCER.listeners:
            msg = json.dumps(
                {metric.__class__.__name__: metric.get() for metric in metrics}
            )
            announce.METRICS_ANNOUNCER.announce(utils.format_sse(data=msg))

    def announce_event(self, event, data):
        """
        Announce the event
        """
        if announce.EVENTS_ANNOUNCER.listeners:
            announce.EVENTS_ANNOUNCER.announce(
                utils.format_sse(data=json.dumps(data), event=event)
            )

    def update_metrics(self, prediction, ground_truth):
        """
        Given a prediction, update metrics to reflect it.
        """
        # Update the metrics
        metrics = self.db["metrics"]
        for metric in metrics:
            # If the metrics requires labels but the prediction is a dict, then we need to retrieve the
            # predicted label with the highest probability
            if (
                isinstance(metric, ClassificationMetric)
                and metric.requires_labels
                and isinstance(prediction, dict)
            ):
                # At this point prediction is a dict. It might be empty because no training data has been seen
                if not prediction:
                    continue
                pred = max(prediction, key=prediction.get)
                metric.update(y_true=ground_truth, y_pred=pred)
            else:
                metric.update(y_true=ground_truth, y_pred=prediction)
        self.db["metrics"] = metrics
        return metrics

    def delete_id(self, identifier):
        try:
            del self.db["#%s" % identifier]
        except KeyError:
            pass


# TODO should we init on startup and use one client?
# TRY THIS
