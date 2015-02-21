.. Skosprovider_sqlalchemy documentation master file, created by
   sphinx-quickstart on Thu Oct 24 08:21:49 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SkosProvider_SQLAlchemy
=======================

This library offers an implementation of the 
:class:`skosprovider.providers.VocabularyProvider`
interface that uses a SQLALchemy_ backend. While a 
:class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` is
a read-only interface, the underlying SQLAlchemy_ 
:mod:`domain model <skosprovider_sqlalchemy.models>` is fully 
writeable.

This library is fully integrated into Atramhasis_, an online open source
editor for :term:`SKOS` vocabularies.

.. toctree::
   :maxdepth: 2

   setup
   api
   changes

.. _SQLAlchemy: http://docs.sqlalchemy.org/
.. _Atramhasis: https://atramhasis.readthedocs.org

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

