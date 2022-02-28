from django.contrib.auth.models import User
from django_river_ml import settings
from django_river_ml.signals import create_user_token
from rest_framework.test import APITestCase
from river import datasets, linear_model, preprocessing, naive_bayes, stream

from riverapi.main import Client
from time import sleep

import subprocess
import shutil
import tempfile
import os
import re


here = os.path.abspath(os.path.dirname(__file__))

# Boolean from environment that determines authentication required variable
auth_regex = re.compile('(\w+)[:=] ?"?([^"]+)"?')

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

        # Get all models
        models = self.client.models()
        assert model_name in models["models"]

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
