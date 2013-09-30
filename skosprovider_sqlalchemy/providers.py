# -*- coding: utf-8 -*-

from skosprovider.providers import VocabularyProvider

from skosprovider.skos import (
    Concept,
    Collection
)


class SQLAlchemyProvider(VocabularyProvider):

    def __init__(self, metadata):
        if not 'default_language' in metadata:
            metadata['default_language'] = 'nl'
        super(SQLAlchemyProvider, self).__init__(metadata)

    def get_by_id(self, id):
        pass

    def find(self, query):
        pass

    def get_all(self):
        pass

    def expand_concept(self, id):
        return self.expand(id)

    def expand(self, id):
        pass
