.. _setup:

=====
Setup
=====

Installation
============

Installation of Skosprovider_sqlalchemy is easily done using :command:`pip`.

.. code-block:: bash
   
   $ pip install skosprovider_sqlalchemy

Creating a database
===================

Since Skosprovider_sqlalchemy implements the SkosProvider_ interface with a
relational database as a backend, you first need to create this database.

.. note::

   Because Skosprovider_sqlalchemy uses SQLAlchemy_ as an ORM layer, it's not
   tailored to any specific database. The codebase is continuously tested
   on both SQLite_ and PostgreSQL_. Other databases are untested by us, but as
   long as they are supported by SQLAlchemy_, they should work.


.. _SkosProvider: http://skosprovider.readthedocs.org
.. _SQLAlchemy: http://docs.sqlalchemy.org/
.. _SQLite: http://www.sqlite.org
.. _PostgreSQL: http://www.postgresql.org
