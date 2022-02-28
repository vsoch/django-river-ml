# django-river-ml

[![CI](https://github.com/vsoch/django-river-ml/actions/workflows/main.yml/badge.svg)](https://github.com/vsoch/django-river-ml/actions/workflows/main.yml)
[![PyPI version](https://badge.fury.io/py/django-river-ml.svg)](https://badge.fury.io/py/django-river-ml)

Django models to deploy [river](https://riverml.xyz) online machine learning. 
This is a Django version of [chantilly](https://github.com/online-ml/chantilly) that aims to use the
same overall design. We also include [example clients](examples/) and a test application in [tests](tests).
We also are developing an [API client](https://github.com/vsoch/riverapi) and early work on a specification that can be extended to other
Python based servers intended for river.

See the ⭐️ [Documentation](https://vsoch.github.io/django-river-ml/) ⭐️ to get started!

## Contributors

We use the [all-contributors](https://github.com/all-contributors/all-contributors) 
tool to generate a contributors graphic below.

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://vsoch.github.io"><img src="https://avatars.githubusercontent.com/u/814322?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Vanessasaurus</b></sub></a><br /><a href="https://github.com/vsoch/django-river-ml/commits?author=vsoch" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->


## TODO

- tests
- should we have a server generic client to plug in here instead?
- create client that can easily interact with API
- add some basic set of frontend views?
- do we want a spec? [issue](https://github.com/online-ml/river/issues/845)
- clean up docstrings -> docs and python docs -> envars list and how to define -> pretty docs
- implement more examples?
- add and test authenticated views
- do we want a default interface for something?

