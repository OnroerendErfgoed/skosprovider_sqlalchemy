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

