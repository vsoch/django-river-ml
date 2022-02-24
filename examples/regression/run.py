from river import datasets
from river import linear_model
from river import preprocessing
import dill
import requests


def main():
    # Before using this endpoint, set MODEL_FLAVOR in settings.py to
    # what you want. A production server is intended to serve one consistent
    # model, unlike the demo. Note that all URls must end with a slash
    host = "http://localhost:8000"

    # Upload a model
    model = preprocessing.StandardScaler() | linear_model.LinearRegression()
    r = requests.post(host + "/api/model/", data=dill.dumps(model))
    model_name = r.json()["name"]
    assert r.status_code == 201
    print("Created model %s" % model_name)

    # Train on some data
    for x, y in datasets.TrumpApproval().take(100):
        r = requests.post(
            host + "/api/learn/",
            json={"model": model_name, "features": x, "ground_truth": y},
        )
        assert r.status_code == 201

    # Get the model
    # TODO we need an endpoint to download model (e.g., pickle version)
    # TODO we need to tweak this one for just json stuffs
    # r = requests.get(host + "/api/model/%s/" % model_name)

    # Make predictions
    for x, y in datasets.TrumpApproval().take(10):
        r = requests.post(
            host + "/api/predict/",
            json={"model": model_name, "features": x},
        )
        assert r.status_code == 200
        #result = r.json()
        #print("prediction: %s vs. actual: %s" % (result["prediction"], y))


if __name__ == "__main__":
    main()
