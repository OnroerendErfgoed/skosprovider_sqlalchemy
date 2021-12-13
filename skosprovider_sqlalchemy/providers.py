import logging

from skosprovider.providers import VocabularyProvider
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source
from skosprovider.uri import DefaultUrnGenerator
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from skosprovider_sqlalchemy.models import Collection as CollectionModel
from skosprovider_sqlalchemy.models import Concept as ConceptModel
from skosprovider_sqlalchemy.models import ConceptScheme as ConceptSchemeModel
from skosprovider_sqlalchemy.models import Label as LabelModel
from skosprovider_sqlalchemy.models import Match as MatchModel
from skosprovider_sqlalchemy.models import Thing
from skosprovider_sqlalchemy.models import Visitation

log = logging.getLogger(__name__)


class SQLAlchemyProvider(VocabularyProvider):
    '''
    A :class:`skosprovider.providers.VocabularyProvider` that uses SQLAlchemy
    as backend.
    '''

    _conceptscheme = None
    '''
    The concept scheme, once it has been loaded. Should never be accessed
    directly.
    '''

    expand_strategy = 'recurse'
    '''
    Determines how the expand method will operate. Options are:

    * `recurse`: Determine all narrower concepts by recursivly querying the
      database. Can take a long time for concepts that are at the top of a
      large hierarchy.
    * `visit`: Query the database's
      :class:`Visitation <skosprovider_sqlalchemy.models.Visitation>` table.
      This table contains a nested set representation of each conceptscheme.
      Actually creating the data in this table needs to be scheduled.
    '''

    def __init__(self, metadata, session, **kwargs):
        '''
        Create a new provider

        :param dict metadata: Metadata about the provider. Apart from the usual
        id, a conceptscheme_id can also be passed.
        :param :class:`sqlachemy.orm.session.Session` session: The database
        session. This can also be a callable that returns a Session.
        '''
        if not 'subject' in metadata:
            metadata['subject'] = []
        self.metadata = metadata
        if 'uri_generator' in kwargs:
            self.uri_generator = kwargs.get('uri_generator')
        else:
            self.uri_generator = DefaultUrnGenerator(self.metadata.get('id'))
        try:
            self.session = session()
        except TypeError as e:
            self.session = session
        try:
            self.conceptscheme_id = int(metadata.get(
                'conceptscheme_id', metadata.get('id')
            ))
        except ValueError:
            raise ValueError(
                'Please provide a valid integer for the conceptscheme_id.'
            )
        if 'expand_strategy' in kwargs:
            if kwargs['expand_strategy'] in ['recurse', 'visit']:
                self.expand_strategy = kwargs['expand_strategy']
            else:
                raise ValueError(
                    'Unknown expand strategy.'
                )
        self.allowed_instance_scopes = ['single', 'threaded_thread']

    @property
    def concept_scheme(self):
        if self._conceptscheme is None:
            self._conceptscheme = self._get_concept_scheme()
        return self._conceptscheme

    def _get_concept_scheme(self):
        '''
        Find a :class:`skosprovider.skos.ConceptScheme` for this provider.

        :param id: Id of a conceptscheme.
        :rtype: :class:`skosprovider.skos.ConceptScheme`
        '''
        csm = self.session\
                  .query(ConceptSchemeModel)\
                  .options(joinedload('labels'))\
                  .options(joinedload('notes'))\
                  .options(joinedload('languages'))\
                  .options(joinedload('sources'))\
                  .get(self.conceptscheme_id)
        return ConceptScheme(
            uri=csm.uri,
            labels=[
                Label(l.label, l.labeltype_id, l.language_id)
                for l in csm.labels
            ],
            notes=[
                Note(n.note, n.notetype_id, n.language_id, n.markup)
                for n in csm.notes
            ],
            languages=[
                l.id for l in csm.languages
            ],
            sources=[
                Source(s.citation, s.markup) for s in csm.sources
            ]
        )

    def _from_thing(self, thing):
        '''
        Load one concept or collection from the database.

        :param :class:`skosprovider_sqlalchemy.models.Thing` thing: Thing
            to load.
        '''
        if thing.type and thing.type == 'collection':
            return Collection(
                id=thing.concept_id,
                uri=thing.uri if thing.uri is not None else self.uri_generator.generate(type='collection', id=thing.concept_id),
                concept_scheme=self.concept_scheme,
                labels=[
                    Label(l.label, l.labeltype_id, l.language_id)
                    for l in thing.labels
                ],
                notes=[
                    Note(n.note, n.notetype_id, n.language_id, n.markup)
                    for n in thing.notes
                ],
                sources=[
                    Source(s.citation, s.markup ) for s in thing.sources
                ],
                members=[member.concept_id for member in thing.members] if hasattr(thing, 'members') else [],
                member_of=[member_of.concept_id for member_of in thing.member_of],
                superordinates=[broader_concept.concept_id for broader_concept in thing.broader_concepts],
                infer_concept_relations=thing.infer_concept_relations
            )
        else:
            matches = {}
            for m in thing.matches:
                key = m.matchtype.name[:m.matchtype.name.find('Match')]
                if not key in matches:
                    matches[key] = []
                matches[key].append(m.uri)
            return Concept(
                id=thing.concept_id,
                uri=thing.uri if thing.uri is not None else self.uri_generator.generate(type='concept', id=thing.concept_id),
                concept_scheme=self.concept_scheme,
                labels=[
                    Label(l.label, l.labeltype_id, l.language_id)
                    for l in thing.labels
                ],
                notes=[
                    Note(n.note, n.notetype_id, n.language_id, n.markup)
                    for n in thing.notes
                ],
                sources=[
                    Source(s.citation, s.markup) for s in thing.sources
                ],
                broader=[c.concept_id for c in thing.broader_concepts],
                narrower=[c.concept_id for c in thing.narrower_concepts],
                related=[c.concept_id for c in thing.related_concepts],
                member_of=[member_of.concept_id for member_of in thing.member_of],
                subordinate_arrays=[narrower_collection.concept_id for narrower_collection in thing.narrower_collections],
                matches=matches
            )

    def get_by_id(self, id):
        try:
            thing = self.session\
                        .query(Thing)\
                        .options(joinedload('labels'))\
                        .options(joinedload('notes'))\
                        .options(joinedload('sources'))\
                        .filter(
                            Thing.concept_id == int(id),
                            Thing.conceptscheme_id == self.conceptscheme_id
                        ).one()
        except NoResultFound:
            return False
        return self._from_thing(thing)

    def get_by_uri(self, uri):
        '''Get all information on a concept or collection, based on a
        :term:`URI`.

        This method will only find concepts or collections whose :term:`URI` is
        actually stored in the database. It will not find anything that has
        no :term:`URI` in the database, but does have a matching :term:`URI`
        after generation.

        :rtype: :class:`skosprovider.skos.Concept` or
            :class:`skosprovider.skos.Collection` or `False` if the concept or
            collection is unknown to the provider.
        '''
        try:
            thing = self.session\
                        .query(Thing)\
                        .options(joinedload('labels'))\
                        .options(joinedload('notes'))\
                        .options(joinedload('sources'))\
                        .filter(
                            Thing.uri == uri,
                            Thing.conceptscheme_id == self.conceptscheme_id
                        ).one()
        except NoResultFound:
            return False
        return self._from_thing(thing)

    def _get_id_and_label(self, c, lan):
        '''
        :param skosprovider_sqlalchemy.models.Thing c: A concept or collection.
        :param string lan: A language (eg. "en", "nl", "la", "fr")
        '''
        l = c.label(lan)
        return {
            'id': c.concept_id,
            'uri': c.uri,
            'type': c.type,
            'label': l.label if l is not None else None
        }

    def find(self, query, **kwargs):
        lan = self._get_language(**kwargs)
        model = Thing
        if 'matches' in query:
            match_uri = query['matches'].get('uri', None)
            if not match_uri:
                raise ValueError(
                    'Please provide a URI to match with.'
                )
            model = ConceptModel
            q = self.session\
                    .query(model)\
                    .options(joinedload('labels'))\
                    .join(MatchModel)\
                    .filter(model.conceptscheme_id == self.conceptscheme_id)
            mtype = query['matches'].get('type')
            if mtype and mtype in Concept.matchtypes:
                mtype += 'Match'
                mtypes = [mtype]
                if mtype == 'closeMatch':
                    mtypes.append('exactMatch')
                q = q.filter(
                    MatchModel.uri == match_uri,
                    MatchModel.matchtype_id.in_(mtypes)
                )
            else:
                q = q.filter(MatchModel.uri == match_uri)
        else:
            q = self.session\
                    .query(model)\
                    .options(joinedload('labels'))\
                    .filter(model.conceptscheme_id == self.conceptscheme_id)
            if 'type' in query and query['type'] in ['concept', 'collection']:
                q = q.filter(model.type == query['type'])
        if 'label' in query:
            q = q.filter(
                model.labels.any(
                    LabelModel.label.ilike('%' + query['label'].lower() + '%')
                )
            )
        if 'collection' in query:
            coll = self.get_by_id(query['collection']['id'])
            if not coll or not isinstance(coll, Collection):
                raise ValueError(
                    'You are searching for items in an unexisting collection.'
                )
            if 'depth' in query['collection'] and query['collection']['depth'] == 'all':
                members = self.expand(coll.id)
            else:
                members = coll.members
            q = q.filter(model.concept_id.in_(members))
        all = q.all()
        sort = self._get_sort(**kwargs)
        sort_order = self._get_sort_order(**kwargs)
        return [self._get_id_and_label(c, lan) for c in self._sort(all, sort, lan, sort_order=='desc')]

    def get_all(self, **kwargs):
        all = self.session\
                  .query(Thing)\
                  .options(joinedload('labels'))\
                  .filter(Thing.conceptscheme_id == self.conceptscheme_id)\
                  .all()
        lan = self._get_language(**kwargs)
        sort = self._get_sort(**kwargs)
        sort_order = self._get_sort_order(**kwargs)
        return [self._get_id_and_label(c, lan) for c in self._sort(all, sort, lan, sort_order=='desc')]

    def get_top_concepts(self, **kwargs):
        # get the concepts that have no direct broader concept
        top = self.session\
                  .query(ConceptModel)\
                  .options(joinedload('labels'))\
                  .filter(
                    ConceptModel.conceptscheme_id == self.conceptscheme_id,
                    ConceptModel.broader_concepts == None
                  ).all()
        # check if they have an indirect broader concept
        def _has_higher_concept(c):
            for coll in c.member_of:
                if coll.infer_concept_relations and (coll.broader_concepts or _has_higher_concept(coll)):
                    return True
            return False
        top = [c for c in top if not _has_higher_concept(c)]
        lan = self._get_language(**kwargs)
        sort = self._get_sort(**kwargs)
        sort_order = self._get_sort_order(**kwargs)
        return [self._get_id_and_label(c, lan) for c in self._sort(top, sort, lan, sort_order=='desc')]

    def expand(self, id):
        try:
            thing = self.session\
                        .query(Thing)\
                        .filter(
                            Thing.concept_id == id,
                            Thing.conceptscheme_id == self.conceptscheme_id
                        ).one()
        except NoResultFound:
            return False

        if self.expand_strategy == 'visit':
            return self._expand_visit(thing)
        elif self.expand_strategy == 'recurse':
            return self._expand_recurse(thing)

    def _expand_recurse(self, thing):
        ret = []
        if thing.type == 'collection':
            for m in thing.members:
                ret += self._expand_recurse(m)
        else:
            ret.append(thing.concept_id)
            for n in thing.narrower_concepts:
                ret += self._expand_recurse(n)
            for n in thing.narrower_collections:
                if n.infer_concept_relations:
                    ret += self._expand_recurse(n)
        return list(set(ret))

    def _expand_visit(self, thing):
        if thing.type == 'collection':
            ret = []
            for m in thing.members:
                ret += self._expand_visit(m)
        else:
            try:
                cov = self.session\
                          .query(Visitation.lft, Visitation.rght)\
                          .filter(Visitation.conceptscheme_id == self.conceptscheme_id)\
                          .filter(Visitation.concept_id == thing.id)\
                          .one()
            except NoResultFound:
                return self._expand_recurse(thing)

            ids = self.session\
                      .query(Thing.concept_id)\
                      .join(Visitation)\
                      .filter(Thing.conceptscheme_id == self.conceptscheme_id)\
                      .filter(Visitation.lft.between(cov[0], cov[1]))\
                      .all()
            ret = [id[0] for id in ids]
        return list(set(ret))

    def get_top_display(self, **kwargs):
        '''
        Returns all concepts or collections that form the top-level of a display
        hierarchy.

        As opposed to the :meth:`get_top_concepts`, this method can possibly
        return both concepts and collections.

        :rtype: Returns a list of concepts and collections. For each an
            id is present and a label. The label is determined by looking at
            the `**kwargs` parameter, the default language of the provider
            and falls back to `en` if nothing is present.
        '''
        tco = self.session\
                  .query(ConceptModel)\
                  .options(joinedload('labels'))\
                  .filter(
                    ConceptModel.conceptscheme_id == self.conceptscheme_id,
                    ConceptModel.broader_concepts == None,
                    ConceptModel.member_of == None
                  ).all()
        tcl = self.session\
                  .query(CollectionModel)\
                  .options(joinedload('labels'))\
                  .filter(
                    CollectionModel.conceptscheme_id == self.conceptscheme_id,
                    CollectionModel.broader_concepts == None,
                    CollectionModel.member_of == None
                  ).all()
        res = tco + tcl
        lan = self._get_language(**kwargs)
        sort = self._get_sort(**kwargs)
        sort_order = self._get_sort_order(**kwargs)
        return [self._get_id_and_label(c, lan) for c in self._sort(res, sort, lan, sort_order=='desc')]

    def get_children_display(self, id, **kwargs):
        '''
        Return a list of concepts or collections that should be displayed
        under this concept or collection.

        :param id: A concept or collection id.
        :rtype: A list of concepts and collections. For each an
            id is present and a label. The label is determined by looking at
            the `**kwargs` parameter, the default language of the provider
            and falls back to `en` if nothing is present. If the id does not
            exist, return `False`.
        '''
        try:
            thing = self.session\
                        .query(Thing)\
                        .filter(
                            Thing.concept_id == int(id),
                            Thing.conceptscheme_id == self.conceptscheme_id
                        ).one()
        except NoResultFound:
            return False
        lan = self._get_language(**kwargs)
        res = []
        if thing.type == 'concept':
            if len(thing.narrower_collections) > 0:
                res += thing.narrower_collections
            elif len(thing.narrower_concepts)>0:
                res += thing.narrower_concepts
        if thing.type == 'collection' and hasattr(thing, 'members'):
            res += thing.members
        sort = self._get_sort(**kwargs)
        sort_order = self._get_sort_order(**kwargs)
        return [self._get_id_and_label(c, lan) for c in self._sort(res, sort, lan, sort_order=='desc')]
