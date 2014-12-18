skosprovider_sqlalchemy
=======================

A SQLAlchemy implementation of the skosprovider_ interface.

.. image:: https://travis-ci.org/koenedaele/skosprovider_sqlalchemy.png?branch=master
        :target: https://travis-ci.org/koenedaele/skosprovider_sqlalchemy
.. image:: https://coveralls.io/repos/koenedaele/skosprovider_sqlalchemy/badge.png?branch=master
        :target: https://coveralls.io/r/koenedaele/skosprovider_sqlalchemy
.. image:: https://badge.fury.io/py/skosprovider_sqlalchemy.png
        :target: http://badge.fury.io/py/skosprovider_sqlalchemy

Building the docs
-----------------

More information about this library can be found in `docs`. The docs can be 
built using `Sphinx <http://sphinx-doc.org>`_.

Please make sure you have installed Sphinx in the same environment where 
skosprovider_sqlalchemy is present.

.. code-block:: bash

    # activate your virtual env
    $ pip install -r requirements-dev.txt
    $ cd docs
    $ make html

.. _skosprovider: https://github.com/koenedaele/skosprovider
