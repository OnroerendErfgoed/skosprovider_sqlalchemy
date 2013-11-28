0.1.1 (28-11-2013)
------------------

* Fixed a bug with collection members being passed instead of their ids.
* Fixed another bug where model ids were used instead of concept ids.

0.1.0
-----

* Initial version
* Implementation of a SKOS domain model in SQLAlchemy.
* Implementation of a skosprovider.providers.VocabularyProvider that 
  uses this model.
* Can query a hierarchy recursively or using nested sets.
* Utility function to import a skosprovider.providers.VocabularyProvider
  in a database.

