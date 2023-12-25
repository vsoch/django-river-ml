import os
import re
import shutil
import subprocess
import sys
import tempfile
from time import sleep

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from river import (
    cluster,
    datasets,
    linear_model,
    multiclass,
    naive_bayes,
    preprocessing,
    stream,
)
from riverapi.main import Client

from django_river_ml import settings
from django_river_ml.signals import create_user_token

here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)
sys.path.insert(0, os.path.dirname(here))

# This adds the root of the repository so tests is importable
# This is the same path seen by our server (important)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Our custom model and supporting function
from tests.custom import VariableVocabKMeans, iter_counts  # noqa

# Boolean from environment that determines authentication required variable
auth_regex = re.compile('(\w+)[:=] ?"?([^"]+)"?')  # noqa

# Important: user needs to be created globally to be seen
user, _ = User.objects.get_or_create(username="dinosaur")
token = create_user_token(user)


class APIBaseTests(APITestCase):
    def setUp(self):
        self.process = subprocess.Popen(["python", "manage.py", "runserver"])
        self.tmpdir = tempfile.mkdtemp()
        sleep(2)
        self.client = Client()

    def tearDown(self):
        os.kill(self.process.pid, 9)
        shutil.rmtree(self.tmpdir)

    def test_api_version_check(self):
        info = self.client.info()
        for key in [
            "id",
            "status",
            "name",
            "description",
            "documentationUrl",
            "storage",
            "river_version",
            "version",
        ]:
            assert key in info

    def test_custom_model(self):
        """
        Basic testing of a custom model
        """
        # Instead of numbers, we provide vectors of tokens (or strings)
        X = [
            ["one", "two"],
            ["one", "four"],
            ["one", "zero"],
            ["five", "six"],
            ["seven", "eight"],
            ["nine", "nine"],
        ]

        model = VariableVocabKMeans(n_clusters=2, halflife=0.4, sigma=3, seed=0)
        model_name = self.client.upload_model(model, "custom")
        print("Created model %s" % model_name)

        for i, vocab in enumerate(iter_counts(X)):
            print(f"Learning from {vocab}")
            self.client.learn(model_name, x=vocab)

        # Make predictions
        for i, vocab in enumerate(iter_counts(X)):
            res = self.client.predict(model_name, x=vocab)
            print(res)

        # Note that custom models currently don't support metrics.
        # If you are interested in adding this please open an issue to discuss!

        # Get stats for the model
        stats = self.client.stats(model_name)
        for key in ["predict", "learn"]:
            assert key in stats and isinstance(stats[key], dict)

        assert stats["predict"]["n_calls"] == 6
        assert stats["learn"]["n_calls"] == 6

        # Delete the model to cleanup
        self.client.delete_model(model_name)

    def test_cluster(self):
        """
        Test a basic clustering
        """
        # Upload a model
        X = [[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]]

        model = cluster.KMeans(n_clusters=2, halflife=0.4, sigma=3, seed=0)
        model_name = self.client.upload_model(model, "cluster")
        print("Created model %s" % model_name)

        for i, (x, _) in enumerate(stream.iter_array(X)):
            self.client.learn(model_name, x=x)

        for i, (x, _) in enumerate(stream.iter_array(X)):
            value = self.client.predict(model_name, x=x)
            assert value["model"] == model_name
            assert value["prediction"] in [0, 1]

        # cluster models don't have metrics or stats (yet)
        metrics = self.client.metrics(model_name)
        assert not metrics

        # Get stats for the model
        stats = self.client.stats(model_name)
        for key in ["predict", "learn"]:
            assert key in stats and isinstance(stats[key], dict)

        assert stats["predict"]["n_calls"] == 6
        assert stats["learn"]["n_calls"] == 6

        self.client.delete_model(model_name)

    def test_regression(self):
        """
        Basic testing of a regression model (no auth)
        """
        model = preprocessing.StandardScaler() | linear_model.LinearRegression()

        # Save the model name for other endpoint interaction
        model_name = self.client.upload_model(model, "regression")
        print("Created model %s" % model_name)

        # Train on some data
        for x, y in datasets.TrumpApproval().take(100):
            self.client.learn(model_name, x=x, y=y)

        # Get the model (this is a json representation)
        model_json = self.client.get_model_json(model_name)
        assert isinstance(model_json, dict)
        assert "StandardScaler" in model_json

        # Saves to model-name>.pkl in pwd unless you provide a second arg, dest
        tmpfile = os.path.join(self.tmpdir, "%s-regression.pkl" % model_name)
        assert not os.path.exists(tmpfile)
        self.client.download_model(model_name, tmpfile)
        assert os.path.exists(tmpfile)

        # Make predictions
        for x, y in datasets.TrumpApproval().take(10):
            value = self.client.predict(model_name, x=x)
            assert value["model"] == model_name

        # By default the server will generate an identifier on predict that you can
        # later use to label it. Let's do that for the last predict call!
        identifier = value["identifier"]
        res = self.client.label(label=y, identifier=identifier, model_name=model_name)
        assert res == "Successful label."

        # Get all models
        models = self.client.models()
        assert model_name in models["models"]

        # Get stats and metrics
        assert self.client.stats(model_name)
        assert self.client.metrics(model_name)

        # Get metrics for the model
        metrics = self.client.metrics(model_name)
        for metric in ["MAE", "RMSE", "SMAPE"]:
            assert metric in metrics
            assert metrics[metric] != 0

        # Get stats for the model
        stats = self.client.stats(model_name)
        for key in ["predict", "learn"]:
            assert key in stats and isinstance(stats[key], dict)

        assert stats["predict"]["n_calls"] == 10
        assert stats["learn"]["n_calls"] == 100

        self.client.delete_model(model_name)

    def test_binary(self):
        """
        Testing of a binary model
        """
        model = preprocessing.StandardScaler() | naive_bayes.GaussianNB()

        # Save the model name for other endpoint interaction
        model_name = self.client.upload_model(model, "binary")
        print("Created model %s" % model_name)

        # Train on some data
        X = [[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]]
        Y = [1, 1, 1, 2, 2, 2]

        for x, y in stream.iter_array(X, Y):
            self.client.learn(model_name, x=x, y=y)

        # Make predictions
        for x, y in stream.iter_array(X, Y):
            print(self.client.predict(model_name, x=x))

        # Get metrics for the model
        metrics = self.client.metrics(model_name)
        for metric in ["Accuracy", "LogLoss", "Precision", "Recall", "F1"]:
            assert metric in metrics and metrics[metric] != 0

        # Get stats for the model
        stats = self.client.stats(model_name)
        for key in ["predict", "learn"]:
            assert key in stats and isinstance(stats[key], dict)

        assert stats["predict"]["n_calls"] == 6
        assert stats["learn"]["n_calls"] == 6
        self.client.delete_model(model_name)

    def test_multiclass(self):
        """
        Testing of a multiclass model
        """
        model = preprocessing.StandardScaler() | naive_bayes.GaussianNB()

        dataset = datasets.ImageSegments()
        scaler = preprocessing.StandardScaler()
        ovo = multiclass.OneVsOneClassifier(linear_model.LogisticRegression())
        model = scaler | ovo

        # Save the model name for other endpoint interaction
        model_name = self.client.upload_model(model, "multiclass")
        print("Created model %s" % model_name)

        # Train on some data
        for x, y in dataset.take(100):
            self.client.learn(model_name, x=x, y=y)

        # Make predictions
        for x, y in dataset.take(100):
            print(self.client.predict(model_name, x=x))

        # Get metrics for the model
        metrics = self.client.metrics(model_name)
        for metric in [
            "Accuracy",
            "CrossEntropy",
            "MacroPrecision",
            "MacroRecall",
            "MacroF1",
            "MicroPrecision",
            "MicroRecall",
            "MicroF1",
        ]:
            assert metric in metrics
            if metric != "CrossEntropy":
                assert metrics[metric] != 0

        # Get stats for the model
        stats = self.client.stats(model_name)
        for key in ["predict", "learn"]:
            assert key in stats and isinstance(stats[key], dict)

        assert stats["predict"]["n_calls"] == 100
        assert stats["learn"]["n_calls"] == 100

        self.client.delete_model(model_name)

    def test_authenticated(self):
        """
        Testing of a regression model (with auth)
        """
        self.client.token = token
        self.client.username = user.username
        settings.DISABLE_AUTHENTICATION = False

        model = preprocessing.StandardScaler() | linear_model.LinearRegression()

        # Save the model name for other endpoint interaction
        model_name = self.client.upload_model(model, "regression")
        print("Created model %s" % model_name)

        # Train on some data
        for x, y in datasets.TrumpApproval().take(100):
            self.client.learn(model_name, x=x, y=y)

        # Get the model (this is a json representation)
        model_json = self.client.get_model_json(model_name)
        assert isinstance(model_json, dict)
        assert "StandardScaler" in model_json

        # Saves to model-name>.pkl in pwd unless you provide a second arg, dest
        tmpfile = os.path.join(self.tmpdir, "%s-auth.pkl" % model_name)
        assert not os.path.exists(tmpfile)
        self.client.download_model(model_name, tmpfile)
        assert os.path.exists(tmpfile)

        # Make predictions
        for x, y in datasets.TrumpApproval().take(10):
            value = self.client.predict(model_name, x=x)
            assert value["model"] == model_name

        # Get all models
        models = self.client.models()
        assert model_name in models["models"]
