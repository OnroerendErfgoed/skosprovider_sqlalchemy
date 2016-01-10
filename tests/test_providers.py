# -*- coding: utf-8 -*-

import pytest
from skosprovider.uri import UriPatternGenerator
from skosprovider_sqlalchemy.models import Initialiser

from skosprovider_sqlalchemy.providers import (
    SQLAlchemyProvider
)
from tests import DBTestCase
from tests.conftest import create_data, create_visitation
from skosprovider_sqlalchemy.models import (
    Base
)


class TestSQLAlchemyProvider(DBTestCase):

    def setUp(self):
        Base.metadata.create_all(self.engine)
        self.session = self.session_maker()
        Initialiser(self.session).init_all()
        create_data(self.session)
        self.provider = SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 1},
            self.session_maker,
            uri_generator=UriPatternGenerator('urn:x-skosprovider-sa:test:%s')
        )

    def tearDown(self):
        self.session.rollback()
        self.session.close_all()
        Base.metadata.drop_all(self.engine)

    def test_default_recurse_strategy(self):
        assert 'recurse' == self.provider.expand_strategy

    def test_override_expand_strategy(self):
        # Set up provider
        provider = SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 1},
            self.session_maker,
            expand_strategy='visit'
        )
        assert 'visit' == provider.expand_strategy

    def test_set_invalid_expand_strategy(self):
        with pytest.raises(ValueError):
            SQLAlchemyProvider(
                {'id': 'SOORTEN', 'conceptscheme_id': 1},
                self.session_maker,
                expand_strategy='invalid'
            )

    def test_provider_without_cs_id(self):
        with pytest.raises(ValueError):
            SQLAlchemyProvider(
                {'id': 'SOORTEN'},
                self.session_maker
            )

    def test_get_vocabulary_id(self):
        assert 'SOORTEN' == self.provider.get_vocabulary_id()

    def test_set_uri_generator(self):
        from skosprovider.uri import UriPatternGenerator
        # Set up provider
        provider = SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 1},
            self.session_maker,
            uri_generator=UriPatternGenerator('http://id.example.com/trees/%s')
        )
        assert 'http://id.example.com/trees/1' == provider.uri_generator.generate(id=1)

    def test_gen_uri(self):
        from skosprovider_sqlalchemy.models import Concept, ConceptScheme
        from skosprovider.uri import UriPatternGenerator
        # Set up provider
        provider = SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 99},
            self.session_maker,
            uri_generator=UriPatternGenerator('http://id.example.com/trees/%s')
        )
        c1 = Concept(concept_id=1, conceptscheme=ConceptScheme(id=99))
        session = self.session_maker()
        session.add(c1)
        session.commit()
        assert c1.uri is None
        c2 = provider.get_by_id(1)
        assert c2.uri == 'http://id.example.com/trees/1'

    def test_concept_scheme(self):
        from skosprovider.skos import (
            ConceptScheme
        )
        cs = self.provider.concept_scheme
        assert isinstance(cs, ConceptScheme)
        assert 'urn:x-skosprovider:test' == cs.uri
        assert 2 == len(cs.languages)
        assert 'en' in cs.languages

    def test_get_concept_by_id(self):
        from skosprovider.skos import Concept

        con = self.provider.get_by_id(1)
        assert isinstance(con, Concept)
        assert 1 == con.id
        assert [3] == con.related
        assert [4] == con.narrower
        assert [2] == con.subordinate_arrays

    def test_concept_has_concept_scheme(self):
        from skosprovider.skos import (
            ConceptScheme
        )
        con = self.provider.get_by_id(1)
        assert isinstance(con.concept_scheme, ConceptScheme)
        assert 'urn:x-skosprovider:test' == con.concept_scheme.uri

    def test_get_concept_by_id_string(self):
        from skosprovider.skos import Concept

        con = self.provider.get_by_id('1')
        assert isinstance(con, Concept)
        assert 1 == con.id
        assert [3] == con.related
        assert [4] == con.narrower
        assert [2] == con.subordinate_arrays

    def test_get_unexisting_by_id(self):
        con = self.provider.get_by_id(404)
        assert not con

    def test_get_concept_by_uri(self):
        cona = self.provider.get_by_id(1)
        conb = self.provider.get_by_uri('urn:x-skosprovider:test:1')
        assert cona.id == conb.id
        assert cona.uri == conb.uri

    def test_get_unexisting_by_uri(self):
        con = self.provider.get_by_uri('urn:x-skosprovider:test:404')
        assert not con

    def test_concept_has_correct_note(self):
        from skosprovider.skos import Note

        cath = self.provider.get_by_id(4)
        assert len(cath.notes) == 1
        assert isinstance(cath.notes[0], Note)

    def test_concept_has_matches(self):
        cath = self.provider.get_by_id(4)
        assert len(cath.matches.keys()) == 5
        assert len(cath.matches['close']) == 1
        assert cath.matches['close'][0] == 'http://vocab.getty.edu/aat/300007501'

    def test_get_collection_by_id(self):
        from skosprovider.skos import Collection

        col = self.provider.get_by_id(2)
        assert isinstance(col, Collection)
        assert 2 == col.id
        assert [4] == col.members
        assert [1] == col.superordinates

    def test_collection_has_no_matches(self):
        col = self.provider.get_by_id(2)
        assert not hasattr(col, 'matches')

    def test_get_collection_by_uri(self):
        from skosprovider.skos import Collection

        cola = self.provider.get_by_id(2)
        colb = self.provider.get_by_uri('urn:x-skosprovider:test:2')
        assert isinstance(colb, Collection)
        assert cola.id == colb.id
        assert cola.uri == colb.uri

    def test_get_all(self):
        all = self.provider.get_all()
        assert len(all) == 5
        assert {
                   'id': 1,
                   'uri': 'urn:x-skosprovider:test:1',
                   'type': 'concept',
                   'label': 'Churches'
               } in all

        assert {
                   'id': 2,
                   'uri': 'urn:x-skosprovider:test:2',
                   'type': 'collection',
                   'label': 'Churches by function'
               } in all

        assert {
                   'id': 3,
                   'uri': 'urn:x-skosprovider:test:3',
                   'type': 'concept',
                   'label': 'Chapels'
               } in all

        assert {
                   'id': 4,
                   'uri': 'urn:x-skosprovider:test:4',
                   'type': 'concept',
                   'label': 'Cathedrals'
               } in all

        assert {
                   'id': 5,
                   'uri': 'urn:x-skosprovider:test:5',
                   'type': 'concept',
                   'label': 'Boomkapellen'
               } in all

    def test_get_all_sorted_id_desc(self):
        all = self.provider.get_all(sort='id', sort_order='desc')
        assert len(all) == 5
        assert [5, 4, 3, 2, 1] == [c['id'] for c in all]

    def test_get_all_sorted_label(self):
        all = self.provider.get_all(sort='label')
        assert len(all) == 5
        assert [
            'Boomkapellen', 'Cathedrals',
            'Chapels', 'Churches',
            'Churches by function'
        ] == [c['label'] for c in all]

    def test_get_all_sorted_sortlabel_desc(self):
        all = self.provider.get_all(sort='sortlabel', sort_order='desc')
        assert len(all) == 5
        assert [
            'Churches',
            'Chapels',
            'Cathedrals',
            'Boomkapellen',
            'Churches by function',
        ] == [c['label'] for c in all]

    def test_get_top_concepts(self):
        all = self.provider.get_top_concepts()
        assert len(all) == 2

        assert {
                   'id': 1,
                   'uri': 'urn:x-skosprovider:test:1',
                   'type': 'concept',
                   'label': 'Churches'
               } in all

        assert {
                   'id': 3,
                   'uri': 'urn:x-skosprovider:test:3',
                   'type': 'concept',
                   'label': 'Chapels'
               } in all

    def test_get_top_concepts_sort_uri_desc(self):
        all = self.provider.get_top_concepts(sort='uri', sort_order='desc')
        assert len(all) == 2

        assert [
            'urn:x-skosprovider:test:3',
            'urn:x-skosprovider:test:1',
        ] == [c['uri'] for c in all]

    def test_get_top_display(self):
        all = self.provider.get_top_display()
        assert len(all) == 2
        assert {
                   'id': 3,
                   'uri': 'urn:x-skosprovider:test:3',
                   'type': 'concept',
                   'label': 'Chapels'
               } in all

        assert {
                   'id': 1,
                   'uri': 'urn:x-skosprovider:test:1',
                   'type': 'concept',
                   'label': 'Churches'
               } in all

    def test_get_top_display_british_sort_label_desc(self):
        all = self.provider.get_top_display(language='en-GB', sort='label', sort_order='desc')
        assert len(all) == 2

        assert [
            'Churches',
            'Chapels'
        ] == [c['label'] for c in all]

    def test_get_children_display_unexisting(self):
        children = self.provider.get_children_display(700)
        assert not children

    def test_get_children_display_collection(self):
        children = self.provider.get_children_display(2)
        assert len(children) == 1
        assert {
                   'id': 4,
                   'uri': 'urn:x-skosprovider:test:4',
                   'type': 'concept',
                   'label': 'Cathedrals'
               } in children

    def test_get_children_display_collection_sort_id(self):
        children = self.provider.get_children_display(2, sort='id')
        assert len(children) == 1
        assert {
                   'id': 4,
                   'uri': 'urn:x-skosprovider:test:4',
                   'type': 'concept',
                   'label': 'Cathedrals'
               } in children

    def test_get_children_display_concept_with_narrower_collection(self):
        children = self.provider.get_children_display(1)
        assert len(children) == 1
        assert {
                   'id': 2,
                   'uri': 'urn:x-skosprovider:test:2',
                   'type': 'collection',
                   'label': 'Churches by function'
               } in children

    def test_get_children_display_concept_with_narrower_concept(self):
        children = self.provider.get_children_display(3)
        assert len(children) == 1
        assert {
                   'id': 5,
                   'uri': 'urn:x-skosprovider:test:5',
                   'type': 'concept',
                   'label': 'Boomkapellen'
               } in children

    def test_get_children_display_concept_with_no_narrower(self):
        children = self.provider.get_children_display(4)
        assert len(children) == 0

    def test_find_all(self):
        all = self.provider.find({})
        assert len(all) == 5

    def test_find_type_all(self):
        all = self.provider.find({'type': 'all'})
        assert len(all) == 5

    def test_find_type_concept(self):
        all = self.provider.find({'type': 'concept'})
        assert len(all) == 4
        assert {
                   'id': 2,
                   'uri': 'urn:x-skosprovider:test:2',
                   'type': 'collection',
                   'label': 'Churches by function'
               } not in all

    def test_find_type_concept_sorted_uri_desc(self):
        all = self.provider.find({'type': 'concept'}, sort='uri', sort_order='desc')
        assert len(all) == 4
        assert [
            'urn:x-skosprovider:test:5', 
            'urn:x-skosprovider:test:4', 
            'urn:x-skosprovider:test:3', 
            'urn:x-skosprovider:test:1', 
            ] == [c['uri'] for c in all]

    def test_find_type_collection(self):
        all = self.provider.find({'type': 'collection'})
        assert len(all) == 1
        assert {
                   'id': 2,
                   'uri': 'urn:x-skosprovider:test:2',
                   'type': 'collection',
                   'label': 'Churches by function'
               } in all

    def test_find_label_kerken(self):
        all = self.provider.find({'label': 'kerken'})
        assert len(all) == 1
        assert {
                   'id': 1,
                   'uri': 'urn:x-skosprovider:test:1',
                   'type': 'concept',
                   'label': 'Churches'
               } in all

    def test_find_label_churches_type_concept(self):
        all = self.provider.find({'label': 'churches', 'type': 'concept'})
        assert len(all) == 1
        assert {
                   'id': 1,
                   'uri': 'urn:x-skosprovider:test:1',
                   'type': 'concept',
                   'label': 'Churches'
               } in all

    def test_find_collection_unexisting(self):
        with pytest.raises(ValueError):
            self.provider.find({'collection': {'id': 404}})

    def test_find_collection_2_no_depth(self):
        all = self.provider.find({'collection': {'id': 2}})
        assert len(all) == 1
        assert {
                   'id': 4,
                   'uri': 'urn:x-skosprovider:test:4',
                   'type': 'concept',
                   'label': 'Cathedrals'
               } in all

    def test_expand_concept(self):
        ids = self.provider.expand(1)
        assert [1, 4] == ids

    def test_expand_collection(self):
        ids = self.provider.expand(2)
        assert [4] == ids

    def test_expand_concept_without_narrower(self):
        ids = self.provider.expand(5)
        assert [5] == ids

    def test_expand_unexisting(self):
        ids = self.provider.expand(404)
        assert not ids


class TestSQLAlchemyProviderExpandVisit(DBTestCase):

    def setUp(self):
        Base.metadata.create_all(self.engine)
        self.session = self.session_maker()
        Initialiser(self.session).init_all()
        create_data(self.session)
        create_visitation(self.session)
        self.visitationprovider=SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 1},
            self.session_maker,
            expand_strategy='visit'
        )

    def tearDown(self):
        self.session.rollback()
        self.session.close_all()
        Base.metadata.drop_all(self.engine)

    def test_expand_concept_visit(self):
        ids = self.visitationprovider.expand(1)
        assert ids == [1, 4]

    def test_expand_collection_visit(self):
        ids = self.visitationprovider.expand(2)
        assert ids == [4]

    def test_expand_concept_without_narrower_visit(self):
        ids = self.visitationprovider.expand(4)
        assert ids == [4]

    def test_expand_unexisting_visit(self):
        ids = self.visitationprovider.expand(404)
        assert not ids


class TestSQLAlchemyProviderExpandVisitNoVisitation(DBTestCase):

    def setUp(self):
        Base.metadata.create_all(self.engine)
        self.session = self.session_maker()
        Initialiser(self.session).init_all()
        self.visitationprovider=SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 1},
            self.session_maker,
            expand_strategy='visit'
        )

    def tearDown(self):
        self.session.rollback()
        self.session.close_all()
        Base.metadata.drop_all(self.engine)

    def test_expand_concept(self):
        ids = self.visitationprovider.expand(1)
        assert not ids

    def test_expand_collection_visit(self):
        ids = self.visitationprovider.expand(2)
        assert not ids

    def test_expand_concept_without_narrower_visit(self):
        ids = self.visitationprovider.expand(3)
        assert not ids

    def test_expand_unexisting_visit(self):
        ids = self.visitationprovider.expand(404)
        assert not ids

