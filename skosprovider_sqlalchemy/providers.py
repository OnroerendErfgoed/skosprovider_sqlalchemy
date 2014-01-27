# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from skosprovider.providers import VocabularyProvider

from skosprovider.skos import (
    Concept,
    Collection,
    Label
)

from skosprovider_sqlalchemy.models import (
    Thing,
    Concept as ConceptModel,
    Collection as CollectionModel,
    Label as LabelModel,
    Visitation
)

from sqlalchemy.orm import (
    joinedload,
)

from sqlalchemy.orm.exc import (
    NoResultFound
)


class SQLAlchemyProvider(VocabularyProvider):
    '''
    A :class:`skosprovider.providers.VocabularyProvider` that uses SQLAlchemy
    as backend.
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
        session.
        '''
        super(SQLAlchemyProvider, self).__init__(metadata)
        self.conceptscheme_id = metadata.get(
            'conceptscheme_id', metadata.get('id')
        )
        self.session = session
        if 'expand_strategy' in kwargs:
            if kwargs['expand_strategy'] in ['recurse', 'visit']:
                self.expand_strategy = kwargs['expand_strategy']
            else:
                raise ValueError(
                    'Unknown expand strategy.'
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
                uri=thing.uri,
                labels=[
                    Label(l.label, l.labeltype_id, l.language_id)
                    for l in thing.labels
                ],
                members=[member.concept_id for member in thing.members] if hasattr(thing, 'members') else []
            )
        else:
            return Concept(
                id=thing.concept_id,
                uri=thing.uri,
                labels=[
                    Label(l.label, l.labeltype_id, l.language_id)
                    for l in thing.labels
                ],
                notes=thing.notes if hasattr(thing, 'notes') else [],
                broader=[c.concept_id for c in thing.broader_concepts],
                narrower=[c.concept_id for c in thing.narrower_concepts],
                related=[c.concept_id for c in thing.related_concepts],
            )

    def get_by_id(self, id):
        try:
            thing = self.session\
                        .query(Thing)\
                        .filter(
                            Thing.concept_id == id,
                            Thing.conceptscheme_id == self.conceptscheme_id
                        ).one()
        except NoResultFound:
            return False
        return self._from_thing(thing)

    def get_by_uri(self, uri):
        try:
            thing = self.session\
                        .query(Thing)\
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
            'label': str(l) if l is not None else None
        }

    def find(self, query, **kwargs):
        lan = self._get_language(**kwargs)
        q = self.session\
                .query(Thing)\
                .options(joinedload('labels'))\
                .filter(Thing.conceptscheme_id == self.conceptscheme_id)
        if 'type' in query and query['type'] in ['concept', 'collection']:
            q = q.filter(Thing.type == query['type'])
        if 'label' in query:
            q = q.filter(
                Thing.labels.any(
                    LabelModel.label.ilike('%' + query['label'].lower() + '%')
                )
            )
        if 'collection' in query:
            coll = self.get_by_id(query['collection']['id'])
            if not coll or not isinstance(coll, Collection):
                raise ValueError(
                    'You are searching for items in an unexisting collection.'
                )
            q = q.filter(
                Thing.collections.any(Thing.concept_id == coll.id)
            )
        all = q.all()
        return [self._get_id_and_label(c, lan) for c in all]

    def get_all(self, **kwargs):
        all = self.session\
                  .query(Thing)\
                  .options(joinedload('labels'))\
                  .filter(Thing.conceptscheme_id == self.conceptscheme_id)\
                  .all()
        lan = self._get_language(**kwargs)
        return [self._get_id_and_label(c, lan) for c in all]

    def get_top_concepts(self, **kwargs):
        top = self.session\
                  .query(ConceptModel)\
                  .options(joinedload('labels'))\
                  .filter(
                    ConceptModel.conceptscheme_id == self.conceptscheme_id,
                    ConceptModel.broader_concepts == None
                  ).all()
        lan = self._get_language(**kwargs)
        return [self._get_id_and_label(c, lan) for c in top]

    def expand_concept(self, id):
        return self.expand(id)

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
        return list(set(ret))

    def _expand_visit(self, thing):
        if thing.type == 'collection':
            ret = []
            for m in thing.members:
                try:
                    ret += self._expand_visit(m)
                except TypeError:
                    return False
        else:
            try:
                cov = self.session\
                          .query(Visitation.lft, Visitation.rght)\
                          .filter(Visitation.conceptscheme_id == self.conceptscheme_id)\
                          .filter(Visitation.concept_id == thing.id)\
                          .one()
            except NoResultFound:
                return False

            ids = self.session\
                      .query(Visitation.concept_id)\
                      .filter(Visitation.conceptscheme_id == self.conceptscheme_id)\
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
                    ConceptModel.collections == None
                  ).all()
        tcl = self.session\
                  .query(CollectionModel)\
                  .options(joinedload('labels'))\
                  .filter(
                    CollectionModel.conceptscheme_id == self.conceptscheme_id
                  ).all()
        res = tco + tcl
        lan = self._get_language(**kwargs)
        return [self._get_id_and_label(c, lan) for c in res]

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
        c = self.get_by_id(id)
        if not c:
            return False
        language = self._get_language(**kwargs)
        ret = []
        if isinstance(c, Concept):
            display_children = c.narrower
        else:
            display_children = c.members
        for id in display_children:
            dc = self.get_by_id(id)
            ret.append({'id': dc.id, 'label': dc.label(language).label})
        return ret
