# -*- coding: utf-8 -*-

import pytest

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa


class ModelTestCase(unittest.TestCase):
    pass

class ConceptTests(ModelTestCase):

    def _get_target_class(self):
        from skosprovider_sqlalchemy.models import Concept
        return Concept

    def test_simple(self):
        from skosprovider_sqlalchemy.models import Label
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
        from skosprovider_sqlalchemy.models import Collection
        c3 = Collection(
            id=2,
            concept_id=3
        )
        c2.narrower_collections.add(c3)
        self.assertEqual(1, len(c2.narrower_collections))
        self.assertEqual(1, len(c3.broader_concepts))


class ConceptSchemeTests(ModelTestCase):

    def _get_target_class(self):
        from skosprovider_sqlalchemy.models import ConceptScheme
        return ConceptScheme

    def test_simple(self):
        from skosprovider_sqlalchemy.models import Label
        l = Label('Heritage types', 'prefLabel', 'en')
        c = self._get_target_class()(
            id=1,
            labels=[l]
        )
        self.assertEqual(1, c.id)
        self.assertEqual(l, c.label())


class CollectionTests(ModelTestCase):

    def _get_target_class(self):
        from skosprovider_sqlalchemy.models import Collection
        return Collection

    def _get_concept(self):
        from skosprovider_sqlalchemy.models import Concept, Label
        return Concept(
            id=2,
            concept_id=456,
            labels=[Label('Cathedrals', 'prefLabel', 'en')]
        )

    def test_simple(self):
        from skosprovider_sqlalchemy.models import Label
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
        self.assertEqual(1, len(c.member_of))
        self.assertIn(col, c.member_of)

    def test_duplicate_members(self):
        col = self._get_target_class()(
            id=1,
            concept_id=7
        )
        c = self._get_concept()
        col.members.add(c)
        self.assertEqual(1, len(c.member_of))
        col.members.add(c)
        self.assertEqual(1, len(c.member_of))


class TestLabel:

    def _get_target_class(self):
        from skosprovider_sqlalchemy.models import Label
        return Label

    def test_simple(self):
        l = self._get_target_class()('Kerken', 'prefLabel', 'nl')
        assert 'nl' == l.language_id
        assert 'prefLabel' == l.labeltype_id
        assert 'Kerken' == l.__str__()

    def test_load_objects(self, session):
        l = self._get_target_class()('Kerken', 'prefLabel', 'nl')
        session.add(l)
        session.flush()
        assert 'Dutch' == l.language.name
        assert 'prefLabel' ==l.labeltype.name

    def test_no_language(self, session):
        l = self._get_target_class()('Kerken', 'prefLabel')
        assert None == l.language_id
        assert 'prefLabel' == l.labeltype_id
        assert 'Kerken' == l.__str__()
        session.add(l)
        session.flush()
        assert None == l.language_id
        assert 'prefLabel' == l.labeltype.name


class TestNote:

    def _get_target_class(self):
        from skosprovider_sqlalchemy.models import Note
        return Note

    def test_simple(self):
        n = self._get_target_class()(
            'Een kerk is een religieus gebouw.',
            'definition',
            'nl'
        )
        assert 'nl' == n.language_id
        assert 'definition' == n.notetype_id
        assert 'Een kerk is een religieus gebouw.' == n.__str__()

    def test_load_objects(self, session):
        n = self._get_target_class()(
            'Een kerk is een religieus gebouw.',
            'definition',
            'nl'
        )
        session.add(n)
        session.flush()
        assert 'Dutch' == n.language.name
        assert 'definition' == n.notetype.name

    def test_no_language(self, session):
        n = self._get_target_class()(
            'Een kerk is een religieus gebouw.',
            'definition',
            None
        )
        assert None == n.language_id
        assert 'definition' == n.notetype_id
        assert 'Een kerk is een religieus gebouw.' == n.__str__()
        session.add(n)
        session.flush()
        assert None == n.language
        assert 'definition' == n.notetype.name


class LanguageTests(ModelTestCase):

    def _get_target_class(self):
        from skosprovider_sqlalchemy.models import Language
        return Language

    def test_simple(self):
        l = self._get_target_class()('nl', 'Dutch')
        self.assertEqual('nl', l.id)
        self.assertEqual('Dutch', l.name)
        self.assertEqual('Dutch', l.__str__())


class LabelTypeTests(ModelTestCase):

    def _get_target_class(self):
        from skosprovider_sqlalchemy.models import LabelType
        return LabelType

    def test_simple(self):
        l = self._get_target_class()('prefLabel', 'Preferred label')
        self.assertEqual('prefLabel', l.name)
        self.assertEqual('Preferred label', l.description)
        self.assertEqual('prefLabel', l.__str__())


class NoteTypeTests(ModelTestCase):

    def _get_target_class(self):
        from skosprovider_sqlalchemy.models import NoteType
        return NoteType

    def test_simple(self):
        n = self._get_target_class()('definition', 'A definition.')
        self.assertEqual('definition', n.name)
        self.assertEqual('A definition.', n.description)
        self.assertEqual('definition', n.__str__())


class TestMatchType:

    def _get_target_class(self):
        from skosprovider_sqlalchemy.models import MatchType
        return MatchType

    def test_simple(self):
        m = self._get_target_class()('closeMatch', 'Quite a close call.')
        assert 'closeMatch' == m.name
        assert 'Quite a close call.' == m.description
        assert m.name == m.__str__()


class TestMatch:

    def _get_target_class(self):
        from skosprovider_sqlalchemy.models import Match
        return Match

    def _get_concept(self):
        from skosprovider_sqlalchemy.models import Concept
        return Concept(
            id=1,
            concept_id=1,
            uri='urn:x-skosprovider:birds:8300'
        )

    def test_simple(self):
        m = self._get_target_class()(
            self._get_concept(),
            'closeMatch',
            'urn:x-skosprovider:heron:grey'
        )
        assert 'closeMatch' == m.matchtype_id
        assert 'urn:x-skosprovider:birds:8300' == m.concept.uri
        assert 'urn:x-skosprovider:heron:grey' == m.uri
        assert m.uri == m.__str__()


class LabelFunctionTest(ModelTestCase):

    def _get_fut(self):
        from skosprovider_sqlalchemy.models import label
        return label

    def _get_knokke_heist_nl(self):
        from skosprovider_sqlalchemy.models import Label
        return Label('Knokke-Heist', "prefLabel", 'nl')

    def _get_cnocke_heyst_nl(self):
        from skosprovider_sqlalchemy.models import Label
        return Label('Cnock-Heyst', "altLabel", 'nl')

    def _get_knokke_heist_en(self):
        from skosprovider_sqlalchemy.models import Label
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
