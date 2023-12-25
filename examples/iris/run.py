from river import cluster, feature_extraction, preprocessing, stream
from riverapi.main import Client
from sklearn import datasets


def main():
    # This is the default, just to show how to customize
    cli = Client("http://localhost:8000")

    # Upload a model, this example  uses an sklearn dataset
    model = cluster.DBSTREAM()
    dataset = datasets.load_iris()

    # Save the model name for other endpoint interaction
    model_name = cli.upload_model(model, "cluster")
    print("Created model %s" % model_name)

    # Train on some data
    for xi, yi in stream.iter_sklearn_dataset(dataset):
        res = cli.learn(x=xi, model_name=model_name)

    # Saves to model-name>.pkl in pwd unless you provide a second arg, dest
    # cli.download_model(model_name)

    # Make predictions
    for xi, yi in stream.iter_sklearn_dataset(dataset):
        res = cli.learn(model_name, x=xi)

    # Get stats for the model
    stats = cli.stats(model_name)

    # Get all models
    print(cli.models())

    # Delete the model to cleanup
    cli.delete_model(model_name)


if __name__ == "__main__":
    main()
