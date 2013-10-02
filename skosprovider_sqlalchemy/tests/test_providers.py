# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from skosprovider_sqlalchemy.providers import (
    SQLAlchemyProvider
)

from skosprovider.skos import (
    Concept,
    Collection
)

from . import engine
from sqlalchemy.orm import sessionmaker

class SQLAlchemyProviderTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = engine

    def setUp(self):
        connection = self.engine.connect()
        self.trans = connection.begin()

        # Setting up SQLAlchemy
        from skosprovider_sqlalchemy.models import Base
        Base.metadata.bind = engine
        sm = sessionmaker(bind=engine)
        self.session= sm()

        # Set up testdata
        self._create_test_data()

        # Set up provider
        self.provider = SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 1},
            self.session
        )

    def tearDown(self):
        self.session.close()
        self.trans.rollback()

    def _create_test_data(self):
        from ..models import Concept, ConceptScheme, Collection
        cs = ConceptScheme(
            id = 1
        )
        self.session.add(cs)
        con = Concept(
            id = 1,
            conceptscheme=cs
        )
        self.session.add(con)
        col = Collection(
            id = 2,
            conceptscheme=cs
        )
        self.session.add(col)
        self.session.flush()

    def test_get_vocabulary_id(self):
        self.assertEquals('SOORTEN', self.provider.get_vocabulary_id())

    def test_get_concept_by_id(self):
        con = self.provider.get_by_id(1)
        self.assertIsInstance(con, Concept)
        self.assertEquals(1, con.id)

    def test_get_collection_by_id(self):
        col = self.provider.get_by_id(2)
        self.assertIsInstance(col, Collection)
        self.assertEquals(2, col.id)

    def test_get_all(self):
        all = self.provider.get_all()
        self.assertEquals(2, len(all))
        self.assertIn({'id': 1, 'label': None}, all)
        self.assertIn({'id': 2, 'label': None}, all)
