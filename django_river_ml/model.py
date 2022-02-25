import inspect


def model_to_dict(model):
    """
    Dump a model to json
    """

    def unwrap(params):
        result = {}
        for k, v in params.items():

            # Dict gets unwrapped
            if isinstance(v, dict):
                result[k] = unwrap(v)

            # List or tuple gets unwrapped
            elif isinstance(v, (list, tuple)):
                items = []
                for item in v:
                    if inspect.isclass(item):
                        items.append(item.__name__)
                    elif isinstance(item, dict):
                        unwrapped = unwrap(item)
                        if unwrapped:
                            items.append(unwrapped)
                    else:
                        items.append(str(item))
                result[k] = items

            # Class we derive name
            elif inspect.isclass(k):
                result[v] = k.__name__
            else:
                result[k] = v
        return result

    params = model._get_params()
    return unwrap(params)
