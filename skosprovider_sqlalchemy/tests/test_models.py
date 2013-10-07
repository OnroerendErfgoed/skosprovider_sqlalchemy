# -*- coding: utf-8 -*-

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
        self.session = sm()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()


class ConceptTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import Concept
        return Concept

    def test_simple(self):
        from ..models import Label
        l = Label('Churches', 'prefLabel', 'en')
        c = self._get_target_class()(
            id=1,
            labels=[l]
        )
        self.assertEqual(1, c.id)
        self.assertEqual(l, c.label())

    def test_related(self):
        c1 = self._get_target_class()(
            id=1
        )
        c2 = self._get_target_class()(
            id=2
        )
        c1.related_concepts.append(c2)
        self.session.flush()
        self.assertEqual(1, len(c1.related_concepts))
        self.assertEqual(1, len(c2.related_concepts))
        c2.related_concepts.remove(c1)
        self.assertEqual(0, len(c1.related_concepts))
        self.assertEqual(0, len(c2.related_concepts))

    def test_broader_narrower(self):
        c1 = self._get_target_class()(
            id=1
        )
        c2 = self._get_target_class()(
            id=2
        )
        c1.narrower_concepts.append(c2)
        self.session.flush()
        self.assertEqual(1, len(c1.narrower_concepts))
        self.assertEqual(1, len(c2.broader_concepts))
        c2.broader_concepts.remove(c1)
        self.assertEqual(0, len(c1.narrower_concepts))
        self.assertEqual(0, len(c2.broader_concepts))


class ConceptSchemeTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import ConceptScheme
        return ConceptScheme

    def test_simple(self):
        from ..models import Label
        l = Label('Heritage types', 'prefLabel', 'en')
        c = self._get_target_class()(
            id=1,
            labels=[l]
        )
        self.session.flush()
        self.assertEqual(1, c.id)
        self.assertEqual(l, c.label())


class CollectionTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import Collection
        return Collection

    def _get_concept(self):
        from ..models import Concept, Label
        return Concept(
            id=2,
            labels=[Label('Cathedrals', 'prefLabel', 'en')]
        )

    def test_simple(self):
        from ..models import Label
        l = Label('Churches by function', 'prefLabel', 'en')
        c = self._get_target_class()(
            id=1,
            labels=[l]
        )
        self.assertEqual(1, c.id)
        self.assertEqual(l, c.label())

    def test_members(self):
        col = self._get_target_class()(
            id=1
        )
        c = self._get_concept()
        col.members.append(c)
        self.session.flush()
        self.assertEqual(1, len(c.collections))
        self.assertEqual(col, c.collections[0])


class LabelTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import Label
        return Label

    def test_simple(self):
        l = self._get_target_class()('Kerken', 'prefLabel', 'nl')
        self.assertEqual('nl', l.language_id)
        self.assertEqual('prefLabel', l.labeltype_id)
        self.assertEqual('Kerken', l.__str__())

    def test_load_objects(self):
        l = self._get_target_class()('Kerken', 'prefLabel', 'nl')
        self.session.add(l)
        self.session.flush()
        self.assertEqual('Dutch', l.language.name)
        self.assertEqual('prefLabel', l.labeltype.name)

    def test_no_language(self):
        l = self._get_target_class()('Kerken', 'prefLabel')
        self.assertEqual(None, l.language_id)
        self.assertEqual('prefLabel', l.labeltype_id)
        self.assertEqual('Kerken', l.__str__())
        self.session.add(l)
        self.session.flush()
        self.assertEqual(None, l.language_id)
        self.assertEqual('prefLabel', l.labeltype.name)


class NoteTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import Note
        return Note

    def test_simple(self):
        n = self._get_target_class()(
            'Een kerk is een religieus gebouw.',
            'definition',
            'nl'
        )
        self.assertEqual('nl', n.language_id)
        self.assertEqual('definition', n.notetype_id)
        self.assertEqual('Een kerk is een religieus gebouw.', n.__str__())

    def test_load_objects(self):
        n = self._get_target_class()(
            'Een kerk is een religieus gebouw.',
            'definition',
            'nl'
        )
        self.session.add(n)
        self.session.flush()
        self.assertEqual('Dutch', n.language.name)
        self.assertEqual('defintion', n.labeltype.name)

    def test_no_language(self):
        n = self._get_target_class()(
            'Een kerk is een religieus gebouw.',
            'definition',
            None
        )
        self.assertEqual(None, n.language_id)
        self.assertEqual('definition', n.notetype_id)
        self.assertEqual('Een kerk is een religieus gebouw.', n.__str__())
        self.session.add(n)
        self.session.flush()
        self.assertEqual(None, n.language)
        self.assertEqual('defintion', n.labeltype.name)


class LanguageTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import Language
        return Language

    def test_simple(self):
        l = self._get_target_class()('nl', 'Dutch')
        self.assertEqual('nl', l.id)
        self.assertEqual('Dutch', l.name)
        self.assertEqual('Dutch', l.__str__())


class LabelTypeTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import LabelType
        return LabelType

    def test_simple(self):
        l = self._get_target_class()('prefLabel', 'Preferred label')
        self.assertEqual('prefLabel', l.name)
        self.assertEqual('Preferred label', l.description)
        self.assertEqual('prefLabel', l.__str__())


class NoteTypeTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import NoteType
        return NoteType

    def test_simple(self):
        n = self._get_target_class()('definition', 'A definition.')
        self.assertEqual('definition', n.name)
        self.assertEqual('A definition.', n.description)
        self.assertEqual('definition', n.__str__())


class NoteTests(ModelTestCase):

    def _get_target_class(self):
        from ..models import Note
        return Note

    def test_simple(self):
        n = self._get_target_class()(
            'definition',
            'en',
            'A church is a place of worship for certain religions.'
        )
        self.assertEqual('definition', n.notetype_id)
        self.assertEqual('en', n.language_id)
        self.assertEqual(
            'A church is a place of worship for certain religions.',
            n.note
        )
