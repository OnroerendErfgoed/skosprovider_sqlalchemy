# -*- coding: utf-8 -*-

import os
import csv

import unittest

from . import engine

from sqlalchemy.orm import sessionmaker

from skosprovider_sqlalchemy.utils import (
    import_provider
)


class UtilsTestCase(unittest.TestCase):

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
        self.session = sm()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()


class ImportProviderTests(UtilsTestCase):

    def _get_cs(self):
        from skosprovider_sqlalchemy.models import (
            ConceptScheme as ConceptSchemeModel
        )
        return ConceptSchemeModel(
            id=1
        )

    def test_empty_provider(self):
        from skosprovider.providers import DictionaryProvider
        p = DictionaryProvider({'id':'EMPTY'},[])
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(p, cs, self.session)
        self.assertEqual(1, len(self.session.new))

    def test_menu(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel
        )
        from skosprovider.providers import (
            SimpleCsvProvider
        )
        ifile = open(
            os.path.join(os.path.dirname(__file__), 'data', 'menu.csv'),
            "r"
        )
        reader = csv.reader(ifile)
        csvprovider = SimpleCsvProvider(
            {'id': 'MENU'},
            reader
        )
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(csvprovider, cs, self.session)
        ifile.close()
        self.assertEqual(24, len(self.session.new))
        lobster = self.session.query(ConceptModel).get(11)
        self.assertEqual(11, lobster.id)
        self.assertEqual('Lobster Thermidor', str(lobster.label()))
        self.assertEqual(1, len(lobster.notes))
