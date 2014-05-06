# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

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
            concept_id=1,
            labels=[l]
        )
        self.assertEqual(1, c.id)
        self.assertEqual(l, c.label())

    def test_related(self):
        c1 = self._get_target_class()(
            id=1,
            concept_id=1
        )
        c2 = self._get_target_class()(
            id=2,
            concept_id=2
        )
        c1.related_concepts.add(c2)
        self.session.flush()
        self.assertEqual(1, len(c1.related_concepts))
        self.assertIn(c2, c1.related_concepts)
        self.assertEqual(1, len(c2.related_concepts))
        self.assertIn(c1, c2.related_concepts)
        c2.related_concepts.remove(c1)
        self.assertEqual(0, len(c1.related_concepts))
        self.assertEqual(0, len(c2.related_concepts))

    def test_related_no_duplicates(self):
        c1 = self._get_target_class()(
            id=1
        )
        c2 = self._get_target_class()(
            id=2
        )
        c1.related_concepts.add(c2)
        self.session.flush()
        self.assertEqual(1, len(c1.related_concepts))
        self.assertIn(c2, c1.related_concepts)
        self.assertEqual(1, len(c2.related_concepts))
        self.assertIn(c1, c2.related_concepts)
        c2.related_concepts.add(c1)
        self.assertEqual(1, len(c1.related_concepts))
        self.assertEqual(1, len(c2.related_concepts))

    def test_broader_narrower(self):
        c1 = self._get_target_class()(
            id=1,
            concept_id=1
        )
        c2 = self._get_target_class()(
            id=2,
            concept_id=2
        )
        c1.narrower_concepts.add(c2)
        self.session.flush()
        self.assertEqual(1, len(c1.narrower_concepts))
        self.assertEqual(1, len(c2.broader_concepts))
        c2.broader_concepts.remove(c1)
        self.assertEqual(0, len(c1.narrower_concepts))
        self.assertEqual(0, len(c2.broader_concepts))

    def test_broader_narrower_duplicate(self):
        c1 = self._get_target_class()(
            id=1,
            concept_id=2
        )
        c2 = self._get_target_class()(
            id=2,
            concept_id=3
        )
        c1.narrower_concepts.add(c2)
        self.session.flush()
        self.assertEqual(1, len(c1.narrower_concepts))
        self.assertEqual(1, len(c2.broader_concepts))
        c2.broader_concepts.add(c1)
        self.assertEqual(1, len(c1.narrower_concepts))
        self.assertEqual(1, len(c2.broader_concepts))

    def test_broader_narrower_collection(self):
        c1 = self._get_target_class()(
            id=1,
            concept_id=2
        )
        c2 = self._get_target_class()(
            id=7,
            concept_id=253
        )
        from ..models import Collection
        c3 = Collection(
            id=2,
            concept_id=3
        )
        c2.narrower_collections.add(c3)
        self.session.flush()
        self.assertEqual(1, len(c2.narrower_collections))
        self.assertEqual(1, len(c3.broader_concepts))


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
            concept_id=456,
            labels=[Label('Cathedrals', 'prefLabel', 'en')]
        )

    def test_simple(self):
        from ..models import Label
        l = Label('Churches by function', 'prefLabel', 'en')
        c = self._get_target_class()(
            id=1,
            concept_id=253,
            labels=[l]
        )
        self.assertEqual(1, c.id)
        self.assertEqual(l, c.label())

    def test_members(self):
        col = self._get_target_class()(
            id=1,
            concept_id=1
        )
        c = self._get_concept()
        col.members.add(c)
        self.session.flush()
        self.assertEqual(1, len(c.collections))
        self.assertIn(col, c.collections)

    def test_duplicate_members(self):
        col = self._get_target_class()(
            id=1,
            concept_id=7
        )
        c = self._get_concept()
        col.members.add(c)
        self.session.flush()
        self.assertEqual(1, len(c.collections))
        col.members.add(c)
        self.assertEqual(1, len(c.collections))


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
        self.assertEqual('definition', n.notetype.name)

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
        self.assertEqual('definition', n.notetype.name)


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


class LabelFunctionTest(ModelTestCase):

    def _get_fut(self):
        from ..models import label
        return label

    def _get_knokke_heist_nl(self):
        from ..models import Label
        return Label('Knokke-Heist', "prefLabel", 'nl')

    def _get_cnocke_heyst_nl(self):
        from ..models import Label
        return Label('Cnock-Heyst', "altLabel", 'nl')

    def _get_knokke_heist_en(self):
        from ..models import Label
        return Label('Knocke-Heyst', "prefLabel", 'en')

    def test_label_empty(self):
        label = self._get_fut()
        self.assertEqual(None, label([]))
        self.assertEqual(None, label([], 'nl'))
        self.assertEqual(None, label([], None))

    def test_label_pref(self):
        label = self._get_fut()
        kh = self._get_knokke_heist_nl()
        labels = [kh]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl'))
        self.assertEqual(kh, label(labels, 'en'))
        self.assertEqual(kh, label(labels, None))

    def test_label_pref_nl_and_en(self):
        label = self._get_fut()
        kh = self._get_knokke_heist_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, khen]
        self.assertIn(label(labels), [kh, khen])
        self.assertEqual(kh, label(labels, 'nl'))
        self.assertEqual(khen, label(labels, 'en'))
        self.assertIn(label(labels, None), [kh, khen])

    def test_label_alt(self):
        label = self._get_fut()
        ch = self._get_cnocke_heyst_nl()
        labels = [ch]
        self.assertEqual(ch, label(labels))
        self.assertEqual(ch, label(labels, 'nl'))
        self.assertEqual(ch, label(labels, 'en'))
        self.assertEqual(ch, label(labels, None))

    def test_pref_precedes_alt(self):
        label = self._get_fut()
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        labels = [kh, ch]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl'))
        self.assertEqual(kh, label(labels, 'en'))
        self.assertEqual(kh, label(labels, None))
