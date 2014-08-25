0.2.1 (2014-08-25)
------------------

* Switch to py.test
* Add `Coveralls <https://coveralls.io>`_ support for code coverage.
* Add ability to configure the SQLAlchemy URL used for testing. Allows testing
  on multiple RDBMS systems.
* Run `Travis <https://travis-ci.org>`_ tests for both SQLite and Postgresql.
* Fix a bug in :meth:`skosprovider_sqlalchemy.utils.import_provider` when 
  dealing with narrower collections (#8). [cahytinne]
* Make the provider actually generate a :term:`URI` if there's none in the 
  database.

0.2.0 (2014-05-14)
------------------

* Compatibility with skosprovider 0.3.0
* Implement :meth:`skosprovider.providers.VocabularyProvider.get_by_uri`.
* Implement :meth:`skosprovider.providers.VocabularyProvider.get_top_concepts`.
* Implement :meth:`skosprovider.providers.VocabularyProvider.get_top_display`
  and :meth:`skosprovider.providers.VocabularyProvider.get_children_display`.
* Add a UniqueConstraint(conceptscheme_id, concept_id) to Thing. (#3)
* Rename the `colletions` attribute of :class:`skosprovider_sqlalchemy.models.Thing`
  to `member_of`. (#7)

0.1.2 (2013-12-06)
------------------

* Pinned dependency on skosprovider < 0.3.0
* Pass data to :class:`skosprovider.skos.Concept` using keywords in stead of 
  positions.

0.1.1 (2013-11-28)
------------------

* Fixed a bug with collection members being passed instead of their ids.
* Fixed another bug where model ids were used instead of concept ids.

0.1.0
-----

* Initial version
* Implementation of a SKOS domain model in SQLAlchemy.
* Implementation of a :class:`skosprovider.providers.VocabularyProvider` that 
  uses this model.
* Can query a hierarchy recursively or using nested sets.
* Utility function to import a :class:`skosprovider.providers.VocabularyProvider`
  in a database.

