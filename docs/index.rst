.. Skosprovider_sqlalchemy documentation master file, created by
   sphinx-quickstart on Thu Oct 24 08:21:49 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SkosProvider_SQLAlchemy
=======================

.. warning::

   This package is deprecated. Starting from ``skosprovider`` 2.0.0 the
   functionality of this package has been merged into the main
   `skosprovider <https://github.com/OnroerendErfgoed/skosprovider/>`_
   repository. This package will remain usable with ``skosprovider < 2.0.0``,
   but is no longer actively maintained. It is recommended to upgrade to
   ``skosprovider >= 2.0.0`` and use ``skosprovider_sqlalchemy`` from there.

This library offers an implementation of the
:class:`skosprovider.providers.VocabularyProvider`
interface that uses a SQLALchemy_ backend. While a 
:class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` is
a read-only interface, the underlying SQLAlchemy_ 
:mod:`domain model <skosprovider_sqlalchemy.models>` is fully 
writeable.

This library is fully integrated into Atramhasis_, an online open source
editor for :term:`SKOS` vocabularies.

Support
-------

If you have questions regarding Skosprovider_SQLAlchemy, feel free to contact us.
Any bugs you find or feature requests you have, you can add to our 
`issue tracker <https://github.com/koenedaele/skosprovider_sqlalchemy/issues>`_. 
If you're unsure if something is a bug or intentional, or you just want to have 
a chat about this library or :term:`SKOS` in general, feel free to join the 
`Atramhasis discussion forum <https://groups.google.com/forum/#!forum/atramhasis>`_.
While these are separate software projects, they are being run by the same 
people and they integrate rather tightly.

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

