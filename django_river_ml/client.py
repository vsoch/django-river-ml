from river.metrics.base import ClassificationMetric

import django_river_ml.storage as storage
import django_river_ml.utils as utils
import django_river_ml.announce as announce
import django_river_ml.flavors as flavors
import django_river_ml.settings as settings

import json
import copy
import uuid


class DjangoClient:
    """
    The Django client provides the main interaction between the storage and
    an internal user. It directly wraps the database, and is used by
    RiverClient to return responses to the API. If you need to interact
    with your models from inside of a Django application, use this class.
    """

    def __init__(self):
        self.db = storage.get_db()

    def stats(self, model_name):
        """
        Get stats for a model name. If they don't exist, we return None.
        """
        try:
            stats = self.db[f"stats/{model_name}"]
        except KeyError:
            return None
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

    def delete_id(self, identifier):
        """
        Delete a known identifier (cached prediction) from the database.
        """
        try:
            del self.db["#%s" % identifier]
        except KeyError:
            pass

    def metrics(self, model_name):
        """
        Get metrics from the database for a specific model
        """
        metrics = {}
        try:
            raw = self.db[f"metrics/{model_name}"]
        # Empty metrics is the equivalent of 404
        except KeyError:
            return metrics

        # Handle inf, -inf and nan (not serializable)
        for metric in raw:
            value = metric.get()
            for field in ["inf", "-inf", "nan"]:
                if str(value) == field:
                    value = field
                    break
            metrics[metric.__class__.__name__] = value
        return metrics

    def add_model(self, model, flavor, name=None):
        """
        Add a model by name (e.g., via API post)
        """
        # Validate the model
        ok, error = flavors.check(model, flavor)
        if not ok:
            return False, error
        return True, storage.add_model(model, name=name, flavor=flavor)

    def save_model(self, model, model_name):
        """
        Save a model by name.
        """
        self.db[f"models/{model_name}"] = model

    def get_model(self, name):
        """
        Get a model by name
        """
        if f"models/{name}" in self.db:
            return self.db[f"models/{name}"]

    def delete_model(self, name):
        """
        Delete a model by name.
        """
        keys = [f"models/{name}", f"stats/{name}", f"metrics/{name}", f"flavor/{name}"]
        found = False
        for key in keys:
            if key in self.db:
                del self.db[key]
                found = True
        return found

    def models(self):
        """
        Get models known to a database.
        """
        model_names = sorted(
            [k.split("/", 1)[1] for k in self.db if k.startswith("models/")]
        )
        return model_names

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

    def learn(
        self,
        model_name,
        ground_truth=None,
        prediction=None,
        features=None,
        identifier=None,
    ):
        """
        A learning event takes a learning schema
        """
        # If an ID is given, then retrieve the stored info.
        # This is akin to label, except for label we require the identifier
        # to exist
        try:
            memory = self.db["#%s" % identifier] if identifier else {}
        except KeyError:
            return False, f"No information stored for ID '{identifier}'"

        model_name = memory.get("model", model_name)
        features = memory.get("features", features)
        prediction = memory.get("prediction", prediction)

        # Raise an error if no features are provided
        if features is None:
            return False, "No features are stored and none were provided."

        # Obtain a prediction if none was made earlier
        if prediction is None:
            success, prediction = self.make_prediction(features, model_name)

            # If we aren't successful, second value is exception
            if not success:
                return success, prediction

        # Update metrics, learn one, and announce events for learn event
        return self.finish_learn(
            "learn",
            prediction=prediction,
            features=features,
            ground_truth=ground_truth,
            model_name=model_name,
            identifier=identifier,
        )

    def label(self, label, identifier, model_name):
        """
        Given a previous prediction (we can get with an identifier) add a label.
        """
        # We are required to have the record
        key = "#%s" % identifier
        if key not in self.db:
            return False, f"No information stored for ID '{identifier}'"

        # Unlink predict, we are required to find these!
        memory = self.db["#%s" % identifier]
        name = memory.get("model")
        features = memory.get("features")
        prediction = memory.get("prediction")

        # We are required to have everything
        if not model_name or not features or prediction is None:
            return False, "Missing one of features, model_name, or prediction."

        # Ensure the label is for the intended model
        if name != model_name:
            return (
                False,
                f"{model_name} was provided, but identifier references {name}.",
            )

        # Update metrics, learn one, and announce events for label event
        return self.finish_learn(
            "label",
            prediction=prediction,
            features=features,
            ground_truth=label,
            model_name=model_name,
            identifier=identifier,
        )

    def finish_learn(
        self, event, prediction, features, ground_truth, model_name, identifier=None
    ):
        """
        Finish a learning event. This can either be a prediction 'predict'
        event that was done on the server, or a 'label' event that retrieved
        a previous prediction and then updated metrics or the model.
        """
        metrics = self.update_metrics(prediction, ground_truth, model_name)

        # Update the model (we've already retrieved it in make_prediction
        # by this point so we know it exists!
        model = self.db[f"models/{model_name}"]

        try:
            # unsupervised
            if not ground_truth:
                model = model.learn_one(x=copy.deepcopy(features))
            else:
                model.learn_one(x=copy.deepcopy(features), y=ground_truth)
        except Exception as e:
            return False, repr(e)

        self.save_model(model, model_name)
        self.announce_event(
            event,
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
        return True, "Successful %s." % event

    # Prediction

    def predict(self, features, model_name, identifier):
        """
        Run a prediction
        """
        # Make the prediction
        success, prediction = self.make_prediction(features, model_name)

        if not success:
            return success, prediction

        # Announce the prediction
        self.announce_event(
            "predict",
            {
                "model": model_name,
                "features": features,
                "prediction": prediction,
            },
        )

        # Generate an ID for learning further down the line.
        identifier = identifier or (
            str(uuid.uuid4()) if settings.GENERATE_IDENTIFIERS else None
        )

        # Was an identifier created?
        if identifier:
            self.db["#%s" % identifier] = {
                "model": model_name,
                "features": features,
                "prediction": prediction,
            }
            return True, {
                "model": model_name,
                "prediction": prediction,
                "identifier": identifier,
            }
        return True, {"model": model_name, "prediction": prediction}

    def make_prediction(self, features, model_name):
        """
        Shared function to make a prediction.

        Returns True if successful with a prediction, otherwise
        False and an exception to return to the user.
        """
        try:
            model = self.db[f"models/{model_name}"]
        except KeyError:
            return False, f"No model named '{model_name}'."

        # If we have a model, we will have a flavor!
        flavor = self.db[f"flavor/{model_name}"]

        # We can fallback to secondary prediction functions
        # given that models can be used in different contexts
        for p, pred_func_name in enumerate(flavor.pred_funcs):
            try:
                pred_func = getattr(model, pred_func_name)

                # Always copy because the model might modify the features in-place
                prediction = pred_func(x=copy.deepcopy(features))

                # The unsupervised parts of the model might be updated after a prediction, so we need to store it
                self.db[f"models/{model_name}"] = model

                return True, prediction
            except Exception as e:
                # If we've failed on the last attempt, return failure
                if p == len(flavor.pred_funcs) - 1:
                    return False, repr(e)

    def update_metrics(self, prediction, ground_truth, model_name):
        """
        Given a prediction, update metrics to reflect it.
        """
        # Update the metrics
        metrics = self.db[f"metrics/{model_name}"]

        # At this point prediction is a dict. It might be empty because no training data has been seen
        if not prediction:
            return metrics

        for metric in metrics:

            # If the metrics requires labels but the prediction is a dict, then we need to retrieve the
            # predicted label with the highest probability
            if (
                isinstance(metric, ClassificationMetric)
                and metric.requires_labels
                and isinstance(prediction, dict)
            ):
                pred = max(prediction, key=prediction.get)
                metric.update(y_true=ground_truth, y_pred=pred)

            else:
                # If we use predict_one and get a string back, we can get
                # down here and have metrics that require labels (and we cannot
                # give them a string) so we should skip.
                try:
                    metric.update(y_true=ground_truth, y_pred=prediction)
                except:
                    pass

        self.db[f"metrics/{model_name}"] = metrics
        return metrics


class RiverClient:
    """
    A river client includes shared functions for interacting with storage.
    This implementation was chosen so it can easily be plugged into another
    kind of server without needing to deal with the server-specific requests.
    """

    def __init__(self):
        self.cli = DjangoClient()

    def stats(self, model_name):
        """
        A wrapper to return stats from the database
        """
        stats = self.cli.stats(model_name)
        if not stats:
            return False, f"We don't have stats for model {model_name}"
        return True, stats

    def stream_events(self):
        """
        Stream events from the events announcer.
        """
        messages = announce.EVENTS_ANNOUNCER.listen()
        return self._stream_announcer(messages)

    def stream_metrics(self):
        """
        Stream events from the metrics announcer.
        """
        messages = announce.METRICS_ANNOUNCER.listen()
        return self._stream_announcer(messages)

    def metrics(self, model_name):
        """
        Get metrics from the database for a specific model
        """
        return self.cli.metrics(model_name)

    def add_model(self, model, flavor, name=None):
        """
        Add a model by name (e.g., via API post)
        """
        added, name = self.cli.add_model(model, flavor, name)
        if not added:
            return False, {"message": name}
        return True, {"name": name}

    def get_model(self, name):
        """
        Get a model by name
        """
        return self.cli.get_model(name)

    def delete_model(self, name):
        """
        Delete a model by name.
        """
        return self.cli.delete_model(name)

    def models(self):
        """
        Get models known to a database.
        """
        return {"models": self.cli.models()}

    def _stream_announcer(self, announcer):
        """
        Shared function to stream events from an announcer.
        """
        while True:
            item = announcer.get()  # blocks until a new message arrives
            yield item

    # Learning and Labeling

    def learn(
        self,
        model_name,
        ground_truth=None,
        prediction=None,
        features=None,
        identifier=None,
    ):
        """
        A learning event takes a learning schema
        """
        return self.cli.learn(
            model_name=model_name,
            ground_truth=ground_truth,
            prediction=prediction,
            features=features,
            identifier=identifier,
        )

    def label(self, label, identifier, model_name):
        """
        Given a previous prediction (we can get with an identifier) add a label.
        """
        return self.cli.label(label=label, identifier=identifier, model_name=model_name)

    # Prediction

    def predict(self, features, model_name, identifier):
        """
        Run a prediction
        """
        return self.cli.predict(
            features=features, model_name=model_name, identifier=identifier
        )

    def make_prediction(self, features, model_name):
        """
        Shared function to make a prediction.

        Returns True if successful with a prediction, otherwise
        False and an exception to return to the user.
        """
        return self.cli.make_prediction(features, model_name)

    def delete_id(self, identifier):
        self.cli.delete_id(identifier)
