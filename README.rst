skosprovider_sqlalchemy
=======================

A SQLAlchemy implementation of the skosprovider_ interface.

.. image:: https://img.shields.io/pypi/v/skosprovider_sqlalchemy.svg
        :target: https://pypi.python.org/pypi/skosprovider_sqlalchemy
.. image:: https://readthedocs.org/projects/skosprovider_sqlalchemy/badge/?version=latest
        :target: https://readthedocs.org/projects/skosprovider_sqlalchemy/?badge=latest

.. image:: https://travis-ci.org/koenedaele/skosprovider_sqlalchemy.png?branch=master
        :target: https://travis-ci.org/koenedaele/skosprovider_sqlalchemy
.. image:: https://img.shields.io/coveralls/koenedaele/skosprovider_sqlalchemy.svg
        :target: https://coveralls.io/r/koenedaele/skosprovider_sqlalchemy
.. image:: https://scrutinizer-ci.com/g/koenedaele/skosprovider_sqlalchemy/badges/quality-score.png?b=master
        :target: https://scrutinizer-ci.com/g/koenedaele/skosprovider_sqlalchemy/?branch=master


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
