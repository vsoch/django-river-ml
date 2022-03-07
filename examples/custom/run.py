from riverapi.main import Client

import os
import sys

# This adds the root of the repository so tests is importable
# This is the same path seen by our server (important)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.custom import iter_counts, VariableVocabKMeans


def main():

    # This is the default, just to show how to customize
    cli = Client("http://localhost:8000")

    # Upload a model

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

    model_name = cli.upload_model(model, "custom")
    print("Created model %s" % model_name)

    for i, vocab in enumerate(iter_counts(X)):
        print(f"Learning from {vocab}")
        cli.learn(model_name, x=vocab)

    # Get the model (this is a json representation)
    model_json = cli.get_model_json(model_name)

    # Saves to model-name>.pkl in pwd unless you provide a second arg, dest
    # cli.download_model(model_name)

    # Make predictions
    for i, vocab in enumerate(iter_counts(X)):
        res = cli.predict(model_name, x=vocab)
        print(res)

    # Note that custom models currently don't support metrics.
    # If you are interested in adding this please open an issue to discuss!

    # Get stats for the model
    stats = cli.stats(model_name)

    # Get all models
    print(cli.models())

    # Delete the model to cleanup
    cli.delete_model(model_name)


if __name__ == "__main__":
    main()
