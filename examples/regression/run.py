from river import datasets
from river import linear_model
from river import preprocessing

import json
import dill
import requests


def print_response(r):
    assert r.status_code in [200, 201]
    response = r.json()
    print("%s: %s" % (r.url, json.dumps(response, indent=4)))


def main():
    host = "http://localhost:8000"

    # Upload a model
    model = preprocessing.StandardScaler() | linear_model.LinearRegression()

    # The first post when you upload the model defines the flavor (regression)
    r = requests.post(host + "/api/model/regression/", data=dill.dumps(model))
    print_response(r)
    model_name = r.json()["name"]
    print("Created model %s" % model_name)

    # Train on some data
    for x, y in datasets.TrumpApproval().take(100):
        r = requests.post(
            host + "/api/learn/",
            json={"model": model_name, "features": x, "ground_truth": y},
        )
        assert r.status_code == 201

    # Get the model (this is a json representation)
    r = requests.get(host + "/api/model/%s/" % model_name)
    assert r.status_code == 200
    print(json.dumps(r.json(), indent=4))

    # Get the model (this is a download of the pickled model with dill)
    r = requests.get(host + "/api/model/download/%s/" % model_name)
    assert r.status_code == 200

    # Here is how to save and load
    # with open("%s.pkl" % model_name, 'wb') as f:
    #     for chunk in r:
    #         f.write(chunk)

    # with open("muffled-pancake-9439.pkl", "rb") as fd:
    #    content=pickle.load(fd)

    # Make predictions
    for x, y in datasets.TrumpApproval().take(10):
        r = requests.post(
            host + "/api/predict/",
            json={"model": model_name, "features": x},
        )
        assert r.status_code == 200
        # result = r.json()
        # print("prediction: %s vs. actual: %s" % (result["prediction"], y))

    # See all models
    r = requests.get(host + "/api/models/")
    print_response(r)


if __name__ == "__main__":
    main()
