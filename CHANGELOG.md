# Changelog

This is a manually generated log to track changes to the repository for each release.
Each section should include general headers such as **Implemented enhancements**
and **Merged pull requests**. All closed issued and bug fixes should be
represented by the pull requests that fixed them.
Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes
 - migration guidance
 - changed behaviour

## [main](https://github.com/vsoch/django-river-ml/tree/main)
 - update metrics type to be imported from metrics.base (0.0.21)
 - limited support to store a creme model (0.0.2)
 - adding ability for Django Client to save to pickle (0.0.19)
 - adding sklearn example and simple view to example app (0.0.18)
 - river.metrics.cluster [was removed](https://github.com/online-ml/river/commit/68aa41c32543a77f5aa53895c0c894e63f9ca712) (0.0.17)
 - refactor of client to provide same functions internally (0.0.16)
  - allow user to specify a custom set of urls to expose
  - documentation for DjangoClient (internal client)
 - support for disable of ratelimit (0.0.15)
 - auth token needs to be in same namespace! (0.0.14)
 - support for custom and cluster models (0.0.13)
 - addition of label endpoint (0.0.12)
 - first version that has authentication and tests (0.0.11)
 - skeleton release  (0.0.1)
