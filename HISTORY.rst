0.4.2 (2015-03-02)
------------------

* Make README work better on pypi.
* Fix a further problem with the length of language identifiers. Previous fix
  in 0.3.0 only fixed the length of the identifiers in the languages table,
  but not in the links from the labels and the notes to the language table. 
  [BartSaelen]
* Added some documentation about setting up a database.

0.4.1 (2014-12-18)
------------------

* Fix a bug with the deletion of a Concept not being possible without having
  it's matches deleted first. [BartSaelen]

0.4.0 (2014-10-28)
------------------

* **Major BC break**: A provider is no longer passed a database session, but a
  database session maker. This change was needed to get the provider to function
  properly in threaded web applications. This will mean changing the
  code where you're creating your provider. In the past, you probably called
  a session maker first and then passed the result of this call to the provider.
  Now you should just pass the session maker itself and let the provider create
  the sessions for you.
* Different way of fetching the :class:`~skosprovider.skos.ConceptScheme` 
  for a provider. No longer fetches a conceptscheme at provider instantiation, 
  but when needed. Otherwise we end up with a possibly very long cached version 
  of a conceptscheme.

0.3.0 (2014-10-17)
------------------

* Update to skosprovider 0.4.0.
* Add :class:`~skosprovider.skos.ConceptScheme` information to a provider so it
  can be attached to :class:`~skosprovider.skos.Concept` objects that are 
  handled by the provider.
* Let provider handle superordinates and subordinate arrays.
* Let provider add notes to collections.
* Added a :class:`~skosprovider_sqlalchemy.models.Match` model to handle
  matches. Expand the provider to actually provide information on these matches.
* Expand the field length for language identifiers. IANA suggests that 
  identifiers up to 35 characters should be permitted. Updated our field length
  to 64 to have a bit of an extra buffer.

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

