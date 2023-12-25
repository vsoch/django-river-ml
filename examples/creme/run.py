import os
import sys

from creme import datasets, feature_extraction, neighbors
from riverapi.main import Client


def main():
    # This is the default, just to show how to customize
    cli = Client("http://localhost:8000")

    # Upload a model
    X_y = datasets.Phishing()

    model = neighbors.KNeighborsClassifier()
    model_name = cli.upload_model(model, "creme")

    print("Created model %s" % model_name)

    for X, Y in X_y:
        print(f"Learning from {X}")
        cli.learn(model_name, x=X, y=Y)

    # Get the model (this is a json representation)
    model_json = cli.get_model_json(model_name)

    for X, Y in X_y:
        res = cli.predict(model_name, x=X)
        print(res["prediction"])

    # Saves to model-name>.pkl in pwd unless you provide a second arg, dest
    # cli.download_model(model_name)

    # Get stats for the model
    stats = cli.stats(model_name)

    # Get all models
    print(cli.models())

    # Delete the model to cleanup
    cli.delete_model(model_name)


if __name__ == "__main__":
    main()
