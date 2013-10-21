# -*- coding: utf-8 -*-

import os
import csv

import unittest

from . import engine

from sqlalchemy.orm import sessionmaker

from skosprovider_sqlalchemy.utils import (
    import_provider,
    VisitationCalculator
)

def _get_menu():
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
    ifile.close()
    return csvprovider


def _get_geo():
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


def _get_buildings():
    from skosprovider.providers import DictionaryProvider
    buildings = DictionaryProvider(
        {'id': 'BUILDINGS'},
        [
            {
                'id': '1',
                'labels': [
                    {'type': 'prefLabel', 'language': 'en', 'label': 'Fortifications'}
                ],
                'narrower': [2]
            }, {
                'id': 2,
                'labels': [
                    {'type': 'prefLabel', 'language': 'en', 'label': 'Castle'}
                ],
                'broader': [1, 3]
            }, {
                'id': 3,
                'labels': [
                    {'type': 'prefLabel', 'language': 'en', 'label': 'Habitations'}
                ],
                'narrower': [2, 4]
            }, {
                'id': 4,
                'labels': [
                    {'type': 'prefLabel', 'language': 'en', 'label': 'Hut'}
                ],
                'broader': [3]
            }
        ]
    )
    return buildings


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
        csvprovider = _get_menu()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(csvprovider, cs, self.session)
        self.assertEqual(24, len(self.session.new))
        lobster = self.session.query(ConceptModel)\
                              .filter(ConceptModel.conceptscheme == cs)\
                              .filter(ConceptModel.concept_id == 11)\
                              .one()
        self.assertEqual(11, lobster.id)
        self.assertEqual('Lobster Thermidor', str(lobster.label()))
        self.assertEqual(1, len(lobster.notes))


    def test_geo(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel,
            Collection as CollectionModel
        )
        geoprovider = _get_geo()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(geoprovider, cs, self.session)
        world = self.session.query(ConceptModel)\
                            .filter(ConceptModel.conceptscheme == cs)\
                            .filter(ConceptModel.concept_id == 1)\
                            .one()
        self.assertEqual(1, world.concept_id)
        self.assertEqual('World', str(world.label('en')))
        self.assertEqual(1, len(world.labels))
        self.assertEqual(2, len(world.narrower_concepts))
        dutch = self.session.query(CollectionModel)\
                            .filter(CollectionModel.conceptscheme == cs)\
                            .filter(CollectionModel.concept_id == 333)\
                            .one()
        self.assertEqual(333, dutch.concept_id)
        self.assertEqual('collection', dutch.type)
        self.assertEqual(1, len(dutch.labels))
        self.assertEqual(4, len(dutch.members))
        netherlands = self.session.query(ConceptModel)\
                            .filter(ConceptModel.conceptscheme == cs)\
                            .filter(ConceptModel.concept_id == 10)\
                            .one()
        self.assertEqual(10, netherlands.concept_id)
        self.assertEqual('concept', netherlands.type)
        self.assertEqual(1, len(netherlands.labels))
        self.assertEqual(2, netherlands.broader_concepts.pop().concept_id)
        self.assertEqual(1, len(netherlands.related_concepts))

    def test_buildings(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel,
            Collection as CollectionModel
        )
        buildingprovider = _get_buildings()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(buildingprovider, cs, self.session)
        castle = self.session.query(ConceptModel)\
                             .filter(ConceptModel.conceptscheme == cs)\
                             .filter(ConceptModel.concept_id == 2)\
                             .one()
        self.assertEqual(2, len(castle.broader_concepts))
        hut = self.session.query(ConceptModel)\
                          .filter(ConceptModel.conceptscheme == cs)\
                          .filter(ConceptModel.concept_id == 4)\
                          .one()
        self.assertEqual(1, len(hut.broader_concepts))


class VisitationCalculatorTests(UtilsTestCase):

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
        vc = VisitationCalculator(self.session)
        v = vc.visit(cs)
        self.assertEqual(0, len(v))

    def test_menu(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel
        )
        csvprovider = _get_menu()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(csvprovider, cs, self.session)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        self.assertEqual(11, len(visit))
        for v in visit:
            self.assertEqual(v['lft']+1, v['rght'])
            self.assertEqual(1, v['depth'])

    def test_menu_sorted(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel
        )
        csvprovider = _get_menu()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(csvprovider, cs, self.session)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        self.assertEqual(11, len(visit))
        left = 1
        for v in visit:
            self.assertEqual(v['lft'], left)
            left += 2

    def test_geo(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel,
            Collection as CollectionModel
        )
        geoprovider = _get_geo()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(geoprovider, cs, self.session)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        self.assertEqual(10, len(visit))
        world = visit[0]
        self.assertEqual(1, world['id'])
        self.assertEqual(1, world['lft'])
        self.assertEqual(20, world['rght'])
        self.assertEqual(1, world['depth'])
        for v in visit:
            if v['id'] == 3:
                self.assertEqual(v['lft']+3, v['rght'])
                self.assertEqual(2, v['depth'])
            if v['id'] == 6:
                self.assertEqual(v['lft']+1, v['rght'])
                self.assertEqual(3, v['depth'])

    def test_buildings(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel,
            Collection as CollectionModel
        )
        buildingprovider = _get_buildings()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(buildingprovider, cs, self.session)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        self.assertEqual(5, len(visit))
        # Check that castle is present twice
        ids = [v['id'] for v in visit]
        self.assertEqual(2, ids.count(2))
        for v in visit:
            # Check that fortification has one child
            if v['id'] == 1:
                self.assertEqual(v['lft']+3, v['rght'])
                self.assertEqual(1, v['depth'])
            # Check that habitations has two children
            if v['id'] == 3:
                self.assertEqual(v['lft']+5, v['rght'])
                self.assertEqual(1, v['depth'])
            # Check that castle has no children
            if v['id'] == 2:
                self.assertEqual(v['lft']+1, v['rght'])
                self.assertEqual(2, v['depth'])
