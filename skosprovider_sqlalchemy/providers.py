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
    Label as LabelModel
)

from sqlalchemy.orm import (
    joinedload,
)

from sqlalchemy.orm.exc import (
    NoResultFound
)


class SQLAlchemyProvider(VocabularyProvider):

    def __init__(self, metadata, session):
        super(SQLAlchemyProvider, self).__init__(metadata)
        self.conceptscheme_id = metadata.get(
            'conceptscheme_id', metadata.get('id')
        )
        self.session = session

    def _from_thing(self, thing):
        '''
        Load one concept or collection from the database.

        :param skosprovider_sqlalchemy.models.Thing thing: Thing to load.
        '''
        if thing.type and thing.type == 'collection':
            return Collection(
                thing.concept_id,
                [
                    Label(l.label, l.labeltype_id, l.language_id)
                    for l in thing.labels
                ],
                thing.members if hasattr(thing, 'members') else []
            )
        else:
            return Concept(
                thing.concept_id,
                [
                    Label(l.label, l.labeltype_id, l.language_id)
                    for l in thing.labels
                ],
                thing.notes if hasattr(thing, 'notes') else [],
                [c.id for c in thing.broader_concepts],
                [c.id for c in thing.narrower_concepts],
                [c.id for c in thing.related_concepts],
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
                Thing.collections.any(Thing.concept_id == query['collection']['id'])
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
        ret = []
        if thing.type == 'collection':
            for m in thing.members:
                ret = ret + self.expand(m.id)
        else:
            ret.append(thing.id)
            for n in thing.narrower_concepts:
                ret = ret + self.expand(n.id)
        return list(set(ret))
