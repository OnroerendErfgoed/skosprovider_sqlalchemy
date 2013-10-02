# -*- coding: utf-8 -*-

from skosprovider.providers import VocabularyProvider

from skosprovider.skos import (
    Concept,
    Collection
)

from skosprovider_sqlalchemy.models import (
    Thing,
    Concept as ConceptModel
)


class SQLAlchemyProvider(VocabularyProvider):

    def __init__(self, metadata, session):
        if not 'default_language' in metadata:
            metadata['default_language'] = 'nl'
        super(SQLAlchemyProvider, self).__init__(metadata)
        self.conceptscheme_id = metadata.get('conceptscheme_id', metadata.get('id'))
        self.session = session

    def _from_thing(self, thing):
        if thing.type and thing.type == 'collection':
            return Collection(
                thing.id,
                thing.labels if hasattr(thing, 'labels') else [],
                thing.members if hasattr(thing, 'members') else []
            )
        else:
            return Concept(
                thing.id,
                thing.labels if hasattr(thing, 'labels') else [],
                thing.notes if hasattr(thing, 'notes') else [],
                thing.broader if hasattr(thing, 'broader') else [],
                thing.narrower if hasattr(thing, 'narrower') else [],
                thing.related if hasattr(thing, 'related') else [],
            )

    def get_by_id(self, id):
        thing = self.session\
                    .query(Thing)\
                    .filter(ConceptModel.id == id, 
                            ConceptModel.conceptscheme_id == self.conceptscheme_id
                    ).one()
        return self._from_thing(thing)

    def find(self, query):
        pass

    def get_all(self):
        all = self.session\
                  .query(Thing)\
                  .all()
        return [{'id': c.id, 'label': c.label()} for c in all]

    def expand_concept(self, id):
        return self.expand(id)

    def expand(self, id):
        return [id]
