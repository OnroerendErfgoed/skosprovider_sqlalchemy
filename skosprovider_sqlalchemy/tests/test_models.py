import unittest

from . import engine

from sqlalchemy.orm import sessionmaker

class ModelTestCase(unittest.TestCase):

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

    def tearDown(self):
        self.session.close()
        self.trans.rollback()


class ConceptTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import Concept
        return Concept

    def test_default(self):
        c = self._get_target_class()(
            id=1
        )
        self.assertEqual(1, c.id)


class ConceptSchemeTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import ConceptScheme
        return ConceptScheme

    def test_default(self):
        c = self._get_target_class()(
            id=1
        )
        self.assertEqual(1, c.id)


class CollectionTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import Collection
        return Collection

    def test_default(self):
        c = self._get_target_class()(
            id=1
        )
        self.assertEqual(1, c.id)
