skosprovider_sqlalchemy
=======================

⚠️ This package is deprecated. Use skosprovider_ instead.

Starting from `skosprovider` 2.0.0 the functionality of this package has been
merged into the main `skosprovider <https://github.com/OnroerendErfgoed/skosprovider/>`_
repository. This package will remain usable with ``skosprovider < 2.0.0``, but is
no longer actively maintained. It is recommended to upgrade to
``skosprovider >= 2.0.0`` and use ``skosprovider_sqlalchemy`` from there.

Migrating to skosprovider 2.0.0
-------------------------------

1. Uninstall ``skosprovider_sqlalchemy`` and install ``skosprovider >= 2.0.0``::

       pip uninstall skosprovider_sqlalchemy
       pip install "skosprovider>=2.0.0"

2. Replace any ``skosprovider_sqlalchemy`` imports with their equivalent under
   ``skosprovider`` (see the `skosprovider
   <https://github.com/OnroerendErfgoed/skosprovider/>`_ documentation for the
   full mapping).

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

.. _skosprovider: https://github.com/OnroerendErfgoed/skosprovider

