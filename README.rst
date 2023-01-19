skosprovider_sqlalchemy
=======================

A SQLAlchemy implementation of the skosprovider_ interface.

.. image:: https://img.shields.io/pypi/v/skosprovider_sqlalchemy.svg
        :target: https://pypi.python.org/pypi/skosprovider_sqlalchemy
.. image:: https://readthedocs.org/projects/skosprovider_sqlalchemy/badge/?version=latest
        :target: https://readthedocs.org/projects/skosprovider_sqlalchemy/?badge=latest

.. image:: https://app.travis-ci.com/OnroerendErfgoed/skosprovider_sqlalchemy.svg?branch=develop
        :target: https://app.travis-ci.com/OnroerendErfgoed/skosprovider_sqlalchemy
.. image:: https://img.shields.io/coveralls/OnroerendErfgoed/skosprovider_sqlalchemy.svg
        :target: https://coveralls.io/r/OnroerendErfgoed/skosprovider_sqlalchemy
.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.5795912.svg
        :target: https://doi.org/10.5281/zenodo.5795912


Migrating to skosprovider_sqlalchemy 2.0.0
------------------------------------------
A change in the models has been made which requires a database upgrade.
The "concept" table's "concept_id" column has changed from being an int to a string.

Existing databases will therefor require a small change to update table scheme.
Typically this will look like::

    ALTER TABLE concept ALTER COLUMN concept_id TEXT NOT NULL;


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
