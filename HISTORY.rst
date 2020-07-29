0.6.0 (2020-07-29)
------------------

* Update to the latest skosprovider version and implement the
  `infer_concept_relations` attribute. (#53)
* Add the ability to query on matches in line with the latest 
  skosprovider version. (#57)
* Drop the session decorator that was added in 0.4.0 since it did not fix the 
  issue we wanted it to fix and it added a lot of overhead. A provider should 
  now be passed a :class:`sqlachemy.orm.session.Session` at startup, or a 
  callable that returns such a session. (#64)
* Improved performance of getting the concept_scheme by caching it. (#71)
* Make querying a collection with depth=all possible. Before the provider would
  only provide the direct members of a collection. (#76)
* Drop support for Python 3.4 and 3.5. Add support for Python 3.7 and 3.8. This
  is also the last version to support Python 2. (#62)

0.5.2 (2018-11-13)
------------------

* Update a lot of dependencies.
* Add __str__ implementations to the model classes. (#43)

0.5.1 (2016-10-05)
------------------

* Catch linking errors when importing a provider and turn them into log warning.
  By linking errors we mean cases where one concept has a relation to a
  non-existing other concept. (#25)
* Allow building as wheel.

0.5.0 (2016-08-11)
------------------

* Update to skosprovider 0.6.0
* **Minor BC break**: A :class:`skosprovider_sqlalchemy.models.Language` that gets
  cast to a string, now returns the language's ID (the IANA language
  code),as opposed to the language's description it would previously return.
* **Minor BC break**: The URI attribute has been made required for a 
  :class:`skosprovider_sqlalchemy.models.ConceptScheme`. Before it was optional,
  but it probably would have caused problems with skosprovider anyway.
* Due to the update to skosprovider 0.6.0, a new field `markup`, was added to a
  :class:`skosprovider_sqlalchemy.models.Note`. When upgrading from a previous
  version of `skosprovider_sqlalchemy`, any databases created in that previous
  verions will need to be updated as well. Please add a field called `markup`
  to the `note` table.
* Inline with the skosprovider 0.6.0 update, a `languages` attribute was added
  to :class:`skosprovider_sqlalchemy.models.ConceptScheme`. When upgrading from
  a previous version of `skosprovider_sqlalchemy`, any databases created with
  that previous verions will need to be updated as well. Please add a table
  called `conceptscheme_language` with fields `conceptscheme_id` and
  `language_id`. (#18)
* To comply with the skosprovider 0.6.0 update, the `sources` attribute was
  added to :class:`skosprovider_sqlalchemy.models.Conceptscheme`,
  :class:`skosprovider_sqlalchemy.models.Concept` and :class:`skosprovider_sqlalchemy.models.Collection`.
  When upgrading from a previous version of `skosprovider_sqlalchemy`, any
  databases created with that previous verions will need to be updated as well.
  Please add a table `source` with fields `id`, `citation` and `markup`,
  a table `concept_source` with fields `concept_id` and `source_id` and a
  table `conceptscheme_source` with fields `conceptscheme_id` and `source_id`.
* All methodes that return a list have been modified in line with skosprovider
  0.6.0 to support sorting. Sorting is possible on `id`, `uri`, `label` and
  `sortlabel`. The last two are language dependent. The `sortlabel` allows
  custom sorting of concepts. This can be used to eg. sort concepts representing
  chronological periods in chronological in stead of alphabetical order. (#20)
* To comply with the skosprovider 0.6.0 update, the deprecated
  :meth:`skosprovider_sqlalchemy.providers.SQLAlchemyProvider.expand_concept`
  was removed.
* When importing a provider, check if the languages that are being used in the
  provider are already in our database. If not, validate them and add them to
  the database. In the past the entire import would fail if not all languages had
  previously been added to the database. (#14)
* When importing a provider, try to import as much information as possible about
  the concept_scheme that's attached to the provider. (#19)
* When querying for indvidual an conceptscheme or concept, use `joinedload` to
  reduce the number of queries needed to collect everything. (#15)
* Deprecated the :func:`skosprovider_sqlalchemy.models.label` function. Please
  use :func:`skosprovider.skos.label` from now once, since this function can now
  operate on both :class:`skosprovider.skos.Label` and
  :class:`skosprovider_sqlalchemy.models.Label` instances. This was the reason
  for the BC break in this release.

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

