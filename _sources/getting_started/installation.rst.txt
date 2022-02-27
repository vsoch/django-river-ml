.. _getting_started-installation:

============
Installation
============


Install django-river-ml (note that river can be troublesome with just pip needing
to compile numpy, etc., it's recommended to use conda and we will have a conda package soon).


.. code-block:: console

    conda create --name ml
    conda activate ml
    conda install river
    pip install django-river-ml


or development from the code:

.. code-block:: console

    $ git clone https://github.com/vsoch/django-river-ml
    $ cd django-river-ml   
    $ pip install -e .


Next check out the :ref:`getting_started-user-guide` pages for more detail to use Django River ML.
