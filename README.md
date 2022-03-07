# django-river-ml

[![CI](https://github.com/vsoch/django-river-ml/actions/workflows/main.yml/badge.svg)](https://github.com/vsoch/django-river-ml/actions/workflows/main.yml)
[![PyPI version](https://badge.fury.io/py/django-river-ml.svg)](https://badge.fury.io/py/django-river-ml)

Django models to deploy [river](https://riverml.xyz) online machine learning. 
This is a Django version of [chantilly](https://github.com/online-ml/chantilly) that aims to use the
same overall design. We also include [example clients](https://github.com/vsoch/django-river-ml/tree/main/examples) and a test application in [tests](https://github.com/vsoch/django-river-ml/tree/main/tests). We also are developing an [API client](https://github.com/vsoch/riverapi) and early work on a 
[specification](https://vsoch.github.io/riverapi/getting_started/spec.html) that can be extended to other
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

- should we have a server generic client to plug in here instead?
- add some basic set of frontend views? some kind of sockets?
- work on same thing with FastAPI?
