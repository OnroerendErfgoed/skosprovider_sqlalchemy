# -*- coding: utf-8 -*-

import pytest

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from skosprovider_sqlalchemy.providers import (
    SQLAlchemyProvider
)

class TestSQLAlchemyProvider:

    def test_default_recurse_strategy(self, provider):
        assert 'recurse' == provider.expand_strategy

    def test_override_expand_strategy(self, session):
        # Set up provider
        provider = SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 1},
            session,
            expand_strategy='visit'
        )
        assert 'visit' == provider.expand_strategy

    def test_set_invalid_expand_strategy(self, session):
        with pytest.raises(ValueError):
            SQLAlchemyProvider(
                {'id': 'SOORTEN', 'conceptscheme_id': 1},
                session,
                expand_strategy='invalid'
            )

    def test_get_vocabulary_id(self, provider):
        assert 'SOORTEN' == provider.get_vocabulary_id()

    def test_set_uri_generator(self, session):
        from skosprovider.uri import UriPatternGenerator
        # Set up provider
        provider = SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 1},
            session,
            uri_generator=UriPatternGenerator('http://id.example.com/trees/%s')
        )
        assert 'http://id.example.com/trees/1' == provider.uri_generator.generate(id=1)

    def test_gen_uri(self, session):
        from skosprovider_sqlalchemy.models import Concept, ConceptScheme
        from skosprovider.uri import UriPatternGenerator
        # Set up provider
        provider = SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 1},
            session,
            uri_generator=UriPatternGenerator('http://id.example.com/trees/%s')
        )
        c1 = Concept(concept_id=1, conceptscheme=ConceptScheme(id=1))
        session.add(c1)
        assert c1.uri is None
        c2 = provider.get_by_id(1)
        assert c2.uri == 'http://id.example.com/trees/1'

    def test_get_concept_by_id(self, provider):
        from skosprovider.skos import Concept
        con = provider.get_by_id(1)
        assert isinstance(con, Concept)
        assert 1 == con.id
        assert [3] == con.related
        assert [4] == con.narrower
        assert [2] == con.subordinate_arrays

    def test_get_concept_by_id_string(self, provider):
        from skosprovider.skos import Concept
        con = provider.get_by_id('1')
        assert isinstance(con, Concept)
        assert 1 == con.id
        assert [3] == con.related
        assert [4] == con.narrower
        assert [2] == con.subordinate_arrays

    def test_get_unexisting_by_id(self, provider):
        con = provider.get_by_id(404)
        assert not con

    def test_get_concept_by_uri(self, provider):
        from skosprovider.skos import Concept
        cona = provider.get_by_id(1)
        conb = provider.get_by_uri('urn:x-skosprovider:test:1')
        assert cona.id == conb.id
        assert cona.uri == conb.uri

    def test_get_unexisting_by_uri(self, provider):
        con = provider.get_by_uri('urn:x-skosprovider:test:404')
        assert not con

    def test_concept_has_correct_note(self, provider):
        from skosprovider.skos import Note
        cath = provider.get_by_id(4)
        assert len(cath.notes) == 1
        assert isinstance(cath.notes[0], Note) 

    def test_concept_has_matches(self, provider):
        cath = provider.get_by_id(4)
        assert len(cath.matches.keys()) == 5
        assert len(cath.matches['close']) == 1
        assert cath.matches['close'][0] == 'http://vocab.getty.edu/aat/300007501'

    def test_get_collection_by_id(self, provider):
        from skosprovider.skos import Collection
        col = provider.get_by_id(2)
        assert isinstance(col, Collection)
        assert 2 == col.id
        assert [4] == col.members
        assert [1] == col.superordinates

    def test_collection_has_no_matches(self, provider):
        col = provider.get_by_id(2)
        assert not hasattr(col, 'matches')

    def test_get_collection_by_uri(self, provider):
        from skosprovider.skos import Collection
        cola = provider.get_by_id(2)
        colb = provider.get_by_uri('urn:x-skosprovider:test:2')
        assert isinstance(colb, Collection)
        assert cola.id == colb.id
        assert cola.uri == colb.uri

    def test_get_all(self, provider):
        all = provider.get_all()
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

    def test_get_top_concepts(self, provider):
        all = provider.get_top_concepts()
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

    def test_get_top_display(self, provider):
        all = provider.get_top_display()
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

    def test_get_children_display_unexisting(self, provider):
        children = provider.get_children_display(700)
        assert not children

    def test_get_children_display_collection(self, provider):
        children = provider.get_children_display(2)
        assert len(children) == 1
        assert {
            'id': 4,
            'uri': 'urn:x-skosprovider:test:4',
            'type': 'concept',
            'label': 'Cathedrals'
        } in children

    def test_get_children_display_concept_with_narrower_collection(self, provider):
        children = provider.get_children_display(1)
        assert len(children) == 1
        assert {
            'id': 2,
            'uri': 'urn:x-skosprovider:test:2',
            'type': 'collection',
            'label': 'Churches by function'
        } in children

    def test_get_children_display_concept_with_narrower_concept(self, provider):
        children = provider.get_children_display(3)
        assert len(children) == 1
        assert {
            'id': 5,
            'uri': 'urn:x-skosprovider:test:5',
            'type': 'concept',
            'label': 'Boomkapellen'
        } in children

    def test_get_children_display_concept_with_no_narrower(self, provider):
        children = provider.get_children_display(4)
        assert len(children) == 0

    def test_find_all(self, provider):
        all = provider.find({})
        assert len(all) == 5

    def test_find_type_all(self, provider):
        all = provider.find({'type': 'all'})
        assert len(all) == 5

    def test_find_type_concept(self, provider):
        all = provider.find({'type': 'concept'})
        assert len(all) == 4
        assert {
            'id': 2,
            'uri': 'urn:x-skosprovider:test:2',
            'type': 'collection',
            'label': 'Churches by function'
        } not in all

    def test_find_type_collection(self, provider):
        all = provider.find({'type': 'collection'})
        assert len(all) == 1
        assert {
            'id': 2,
            'uri': 'urn:x-skosprovider:test:2',
            'type': 'collection',
            'label': 'Churches by function'
        } in all

    def test_find_label_kerken(self, provider):
        all = provider.find({'label': 'kerken'})
        assert len(all) == 1
        assert {
            'id': 1,
            'uri': 'urn:x-skosprovider:test:1',
            'type': 'concept',
            'label': 'Churches'
        } in all

    def test_find_label_churches_type_concept(self, provider):
        all = provider.find({'label': 'churches', 'type': 'concept'})
        assert len(all) == 1
        assert {
            'id': 1,
            'uri': 'urn:x-skosprovider:test:1',
            'type': 'concept',
            'label': 'Churches'
        } in all

    def test_find_collection_unexisting(self, provider):
        with pytest.raises(ValueError):
            provider.find({'collection': {'id': 404}})

    def test_find_collection_2_no_depth(self, provider):
        all = provider.find({'collection': {'id': 2}})
        assert len(all) == 1
        assert {
            'id': 4,
            'uri': 'urn:x-skosprovider:test:4',
            'type': 'concept',
            'label': 'Cathedrals'
        } in all

    def test_expand_concept(self, provider):
        ids = provider.expand_concept(1)
        assert [1, 4] == ids

    def test_expand_collection(self, provider):
        ids = provider.expand(2)
        assert [4] == ids

    def test_expand_concept_without_narrower(self, provider):
        ids = provider.expand(5)
        assert [5] == ids

    def test_expand_unexisting(self, provider):
        ids = provider.expand(404)
        assert not ids

@pytest.mark.usefixtures('create_visitation')
class TestSQLAlchemyProviderExpandVisit:

    def test_expand_concept_visit(self, create_visitation, visitationprovider):
        ids = visitationprovider.expand_concept(1)
        assert ids == [1, 4]

    def test_expand_collection_visit(self, create_visitation, visitationprovider):
        ids = visitationprovider.expand(2)
        assert ids == [4]

    def test_expand_concept_without_narrower_visit(self, create_visitation, visitationprovider):
        ids = visitationprovider.expand(4)
        assert ids == [4]

    def test_expand_unexisting_visit(self, create_visitation, visitationprovider):
        ids = visitationprovider.expand(404)
        assert not ids


class TestSQLAlchemyProviderExpandVisitNoVisitation:

    def test_expand_concept(self, visitationprovider):
        ids = visitationprovider.expand_concept(1)
        assert not ids

    def test_expand_collection_visit(self, visitationprovider):
        ids = visitationprovider.expand(2)
        assert not ids

    def test_expand_concept_without_narrower_visit(self, visitationprovider):
        ids = visitationprovider.expand(3)
        assert not ids

    def test_expand_unexisting_visit(self, visitationprovider):
        ids = visitationprovider.expand(404)
        assert not ids
