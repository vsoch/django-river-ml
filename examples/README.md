# Examples

The following examples will show you how to interact with the test application
provided. All examples use the [riverapi](https://github.com/vsoch/riverapi)
library that you can install from pip.

```bash
$ pip install riverapi
```

The subdirectories are named based on the model type. E.g., for
"regression" make sure you set the settings.py `MODEL_FLAVOR` to regression first.
And then start the server:

```bash
$ python manage.py runserver
```

 - [regression](regression)
 - [binary](binary)
 - [multiclass](multiclass)
 - [cluster](cluster)
 - [custom](custom): currently is an example for a custom model (kmeans) 

