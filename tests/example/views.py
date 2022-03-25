from django.shortcuts import render
from django_river_ml.client import DjangoClient
from django.http import JsonResponse
import pandas
from scipy.spatial.distance import pdist, squareform
import sklearn.manifold as manifold


def get_centers(model):
    """
    Helper function to derive centroids from a model
    """
    if hasattr(model, "steps"):
        for step_name, step in model.steps.items():
            if hasattr(step, "centers") and step.centers:
                return step.centers
    elif hasattr(model, "centers") and model.centers:
        return model.centers


def generate_embeddings(centers):
    df = pandas.DataFrame(centers)

    # 200 rows (centers) and N columns (words)
    df = df.transpose()
    df = df.fillna(0)

    # Create a distance matrix
    distance = pandas.DataFrame(
        squareform(pdist(df)), index=list(df.index), columns=list(df.index)
    )

    # Make the tsne (output embeddings go into docs for visual)
    fit = manifold.TSNE(n_components=2)
    embedding = fit.fit_transform(distance)
    emb = pandas.DataFrame(embedding, index=distance.index, columns=["x", "y"])
    emb.index.name = "name"
    return emb.to_dict(orient="records")


def get_centroids(request, name):
    """
    JsonResponse to just retrun centroids
    """
    client = DjangoClient()
    model = client.get_model(name)
    centers = get_centers(model)
    return JsonResponse({"centers": generate_embeddings(centers)})


def index(request):

    # Get a django client
    client = DjangoClient()

    # Get a list of the module names that have cluster centers
    have_centroids = set()
    for model_name in client.models():
        model = client.get_model(model_name)
        if get_centers(model) is not None:
            have_centroids.add(model_name)
    return render(request, "main/index.html", {"have_centroids": have_centroids})
