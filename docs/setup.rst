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
relational database as a backend, you first need to create this database. To
do this, please follow the instructions of your database software. If you're
working with SQLite_, you don't need to do anything.

.. note::

   Because Skosprovider_sqlalchemy uses SQLAlchemy_ as an ORM layer, it's not
   tailored to any specific database. The codebase is continuously tested
   on both SQLite_ and PostgreSQL_. Other databases are untested by us, but as
   long as they are supported by SQLAlchemy_, they should work.

Once your database has been created, you can initialise it with the necessary
database tables that will contain your :term:`SKOS` vocabularies and concepts.

.. code-block:: bash

   $ init_skos_db sqlite:///vocabs.db

Let's have a look at what this script did.

.. code-block:: bash

   $ sqlite3 vocabs.db
   SQLite version 3.7.9 2011-11-01 00:52:41
   Enter ".help" for instructions
   Enter SQL statements terminated with a ";"
   sqlite> .tables
   collection_concept            conceptscheme_note          
   concept                       label                       
   concept_hierarchy_collection  labeltype                   
   concept_hierarchy_concept     language                    
   concept_label                 match                       
   concept_note                  matchtype                   
   concept_related_concept       note                        
   conceptscheme                 notetype                    
   conceptscheme_label           visitation     


Upgrading from skosprovider_sqlalchemy 1.x to 2.x
=================================================

A change in the models has been made which requires a database upgrade.
The "concept" table's "concept_id" column has changed from being an int to a string.

Existing databases will therefor require a small change to update table scheme.
Typically this will look like::

    ALTER TABLE concept ALTER COLUMN concept_id TEXT NOT NULL;

.. _SkosProvider: http://skosprovider.readthedocs.org
.. _SQLAlchemy: http://docs.sqlalchemy.org/
.. _SQLite: http://www.sqlite.org
.. _PostgreSQL: http://www.postgresql.org
