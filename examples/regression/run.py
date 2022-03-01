from river import datasets
from river import linear_model
from river import preprocessing

from riverapi.main import Client


def main():

    # This is the default, just to show how to customize
    cli = Client("http://localhost:8000")

    # Upload a model
    model = preprocessing.StandardScaler() | linear_model.LinearRegression()

    # Save the model name for other endpoint interaction
    model_name = cli.upload_model(model, "regression")
    print("Created model %s" % model_name)

    # Train on some data
    for x, y in datasets.TrumpApproval().take(100):
        cli.learn(model_name, x=x, y=y)

    # Get the model (this is a json representation)
    model_json = cli.get_model_json(model_name)

    # Saves to model-name>.pkl in pwd unless you provide a second arg, dest
    # cli.download_model(model_name)

    # Make predictions
    for x, y in datasets.TrumpApproval().take(10):
        print(cli.predict(model_name, x=x))

    # Get metrics for the model
    metrics = cli.metrics(model_name)

    # Get stats for the model
    stats = cli.stats(model_name)

    # Get all models
    print(cli.models())

    # Delete the model to cleanup
    cli.delete_model(model_name)


if __name__ == "__main__":
    main()
