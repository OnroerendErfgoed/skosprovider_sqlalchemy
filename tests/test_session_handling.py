# -*- coding: utf-8 -*-
import unittest
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from skosprovider_sqlalchemy.models import Base
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from tests.conftest import create_data


class SessionHandlingTest(unittest.TestCase):

    def setUp(self):
        settings = {'sqlalchemy.url': 'sqlite:///:memory:'}
        self.engine = engine_from_config(settings, prefix='sqlalchemy.')
        self.session_maker = sessionmaker(
            bind=self.engine
        )
        Base.metadata.create_all(self.engine)
        session = self.session_maker()
        try:
            create_data(session)
            session.commit()
        except:
            session.rollback()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_init_provider(self):
        provider = SQLAlchemyProvider({'id': 'SOORTEN', 'conceptscheme_id': 1},
                                      self.session_maker)
        self.assertIsNotNone(provider)

    def test_get_by_id(self):
        provider = SQLAlchemyProvider({'id': 'SOORTEN', 'conceptscheme_id': 1},
                                      self.session_maker)
        self.assertIsNotNone(provider)
        concept = provider.get_by_id(10)
        self.assertIsNotNone(concept)