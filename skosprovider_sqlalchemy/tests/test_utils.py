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

    def _get_geo(self):
        from skosprovider.providers import DictionaryProvider
        geo = DictionaryProvider(
            {'id': 'GEOGRAPHY'},
            [
                {
                    'id': '1',
                    'labels': [
                        {'type': 'prefLabel', 'language': 'en', 'label': 'World'}
                    ],
                    'narrower': [2, 3]
                }, {
                    'id': 2,
                    'labels': [
                        {'type': 'prefLabel', 'language': 'en', 'label': 'Europe'}
                    ],
                    'narrower': [4, 5, 10], 'broader': [1]
                }, {
                    'id': 3,
                    'labels': [
                        {
                            'type': 'prefLabel', 'language': 'en',
                            'label': 'North-America'
                        }
                    ],
                    'narrower': [6], 'broader': [1]
                }, {
                    'id': 4,
                    'labels': [
                        {'type': 'prefLabel', 'language': 'en', 'label': 'Belgium'}
                    ],
                    'narrower': [7, 8, 9], 'broader': [2], 'related': [10]
                }, {
                    'id': 5,
                    'labels': [
                        {
                            'type': 'prefLabel', 'language': 'en',
                            'label': 'United Kingdom'
                        }
                    ],
                    'broader': [2]
                }, {
                    'id': 6,
                    'labels': [
                        {
                            'type': 'prefLabel', 'language': 'en',
                            'label': 'United States of America'
                        }
                    ],
                    'broader': [3]
                }, {
                    'id': 7,
                    'labels': [
                        {'type': 'prefLabel', 'language': 'en', 'label': 'Flanders'}
                    ],
                    'broader': [4]
                }, {
                    'id': 8,
                    'labels': [
                        {'type': 'prefLabel', 'language': 'en', 'label': 'Brussels'}
                    ],
                    'broader': [4]
                }, {
                    'id': 9,
                    'labels': [
                        {'type': 'prefLabel', 'language': 'en', 'label': 'Wallonie'}
                    ],
                    'broader': [4]
                }, {
                    'id': 10,
                    'labels': [
                        {'type': 'prefLabel', 'language': 'nl', 'label': 'Nederland'}
                    ],
                    'related': [4]
                }, {
                    'id': '333',
                    'type': 'collection',
                    'labels': [
                        {
                            'type': 'prefLabel', 'language': 'en',
                            'label': 'Places where dutch is spoken'
                        }
                    ],
                    'members': ['4', '7', 8,10]
                }
            ]
        )
        return geo

    def test_geo(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel,
            Collection as CollectionModel
        )
        geoprovider = self._get_geo()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(geoprovider, cs, self.session)
        world = self.session.query(ConceptModel).get(1)
        self.assertEqual(1, world.id)
        self.assertEqual('World', str(world.label('en')))
        self.assertEqual(1, len(world.labels))
        self.assertEqual(2, len(world.narrower_concepts))
        dutch = self.session.query(CollectionModel).get(333)
        self.assertEqual(333, dutch.id)
        self.assertEqual('collection', dutch.type)
        self.assertEqual(1, len(dutch.labels))
        self.assertEqual(4, len(dutch.members))
        netherlands = self.session.query(ConceptModel).get(10)
        self.assertEqual(10, netherlands.id)
        self.assertEqual('concept', netherlands.type)
        self.assertEqual(1, len(netherlands.labels))
        self.assertEqual(2, netherlands.broader_concepts[0].id)
        self.assertEqual(1, len(netherlands.related_concepts))
