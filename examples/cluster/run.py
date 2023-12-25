from river import cluster, stream
from riverapi.main import Client


def main():
    # This is the default, just to show how to customize
    cli = Client("http://localhost:8000")

    # Upload a model
    X = [[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]]

    model = cluster.KMeans(n_clusters=2, halflife=0.4, sigma=3, seed=0)

    model_name = cli.upload_model(model, "cluster")
    print("Created model %s" % model_name)

    for i, (x, _) in enumerate(stream.iter_array(X)):
        res = cli.learn(model_name, x=x)

    # Get the model (this is a json representation)
    model_json = cli.get_model_json(model_name)

    # Saves to model-name>.pkl in pwd unless you provide a second arg, dest
    # cli.download_model(model_name)

    # Make predictions
    for i, (x, _) in enumerate(stream.iter_array(X)):
        res = cli.predict(model_name, x=x)
        print(res)

    # Note that cluster models currently don't have metrics
    metrics = cli.metrics(model_name)
    # If you are interested in adding this please open an issue to discuss!

    # Get stats for the model
    stats = cli.stats(model_name)

    # Get all models
    print(cli.models())

    # Delete the model to cleanup
    cli.delete_model(model_name)


if __name__ == "__main__":
    main()
