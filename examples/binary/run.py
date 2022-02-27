from river import datasets
from river import naive_bayes
from river import preprocessing
from river import stream

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
    model = preprocessing.StandardScaler() | naive_bayes.GaussianNB()
    r = requests.post(host + "/api/model/binary/", data=dill.dumps(model))
    model_name = r.json()["name"]
    print_response(r)
    print("Created model %s" % model_name)

    # Train on some data
    X = [[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]]
    Y = [1, 1, 1, 2, 2, 2]

    for x, y in stream.iter_array(X, Y):
        r = requests.post(
            host + "/api/learn/",
            json={"model": model_name, "features": x, "ground_truth": y},
        )
        print_response(r)

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
    for x, y in stream.iter_array(X, Y):
        r = requests.post(
            host + "/api/predict/",
            json={"model": model_name, "features": x},
        )
        print_response(r)


if __name__ == "__main__":
    main()
