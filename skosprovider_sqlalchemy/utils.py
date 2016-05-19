# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)

from skosprovider.skos import (
    Concept,
    Collection
)

from language_tags import tags

from skosprovider_sqlalchemy.models import (
    Thing as ThingModel,
    Concept as ConceptModel,
    Collection as CollectionModel,
    Label as LabelModel,
    Note as NoteModel,
    Match as MatchModel,
    Language as LanguageModel,
    Source as SourceModel
)


def import_provider(provider, conceptscheme, session):
    '''
    Import a provider into a SQLAlchemy database.

    :param provider: The :class:`skosprovider.providers.VocabularyProvider`
        to import. Since the SQLAlchemy backend uses integers as
        keys, this backend should have id values that can be cast to int.
    :param conceptscheme: A
        :class:`skosprovider_sqlalchemy.models.Conceptscheme` to import
        the provider into. This should be an empty scheme so that there are
        no possible id clashes.
    :param session:  A :class:`sqlalchemy.orm.session.Session`.

    '''

    # Copy information about the scheme
    cs = provider.concept_scheme
    _add_labels(conceptscheme, cs.labels, session)
    _add_notes(conceptscheme, cs.notes, session)
    _add_sources(conceptscheme, cs.sources, session)
    for l in cs.languages:
        language = _check_language(l, session)
        conceptscheme.languages.append(language)

    # First pass: load all concepts and collections
    for stuff in provider.get_all():
        c = provider.get_by_id(stuff['id'])
        if isinstance(c, Concept):
            cm = ConceptModel(
                concept_id=int(c.id),
                uri=c.uri,
                conceptscheme=conceptscheme
            )
        elif isinstance(c, Collection):
            cm = CollectionModel(
                concept_id=int(c.id),
                uri=c.uri,
                conceptscheme=conceptscheme
            )
        _add_labels(cm, c.labels, session)
        _add_notes(cm, c.notes, session)
        _add_sources(cm, c.sources, session)
        if hasattr(c, 'matches'):
            for mt in c.matches:
                matchtype = mt + 'Match'
                for m in c.matches[mt]:
                    match = MatchModel(matchtype_id=matchtype, uri=m)
                    cm.matches.append(match)
        session.add(cm)

    session.flush()

    # Second pass: link
    for stuff in provider.get_all():
        c = provider.get_by_id(stuff['id'])
        if isinstance(c, Concept):
            cm = session.query(ConceptModel) \
                .filter(ConceptModel.conceptscheme_id == conceptscheme.id) \
                .filter(ConceptModel.concept_id == int(c.id)) \
                .one()
            if len(c.narrower) > 0:
                for nc in c.narrower:
                    nc = session.query(ConceptModel) \
                        .filter(ConceptModel.conceptscheme_id == conceptscheme.id) \
                        .filter(ConceptModel.concept_id == int(nc)) \
                        .one()
                    cm.narrower_concepts.add(nc)
            if len(c.subordinate_arrays) > 0:
                for sa in c.subordinate_arrays:
                    sa = session.query(CollectionModel) \
                        .filter(CollectionModel.conceptscheme_id == conceptscheme.id) \
                        .filter(CollectionModel.concept_id == int(sa)) \
                        .one()
                    cm.narrower_collections.add(sa)
            if len(c.related) > 0:
                for rc in c.related:
                    rc = session.query(ConceptModel) \
                        .filter(ConceptModel.conceptscheme_id == conceptscheme.id) \
                        .filter(ConceptModel.concept_id == int(rc)) \
                        .one()
                    cm.related_concepts.add(rc)
        elif isinstance(c, Collection) and len(c.members) > 0:
            cm = session.query(CollectionModel) \
                .filter(ConceptModel.conceptscheme_id == conceptscheme.id) \
                .filter(ConceptModel.concept_id == int(c.id)) \
                .one()
            for mc in c.members:
                mc = session.query(ThingModel) \
                    .filter(ConceptModel.conceptscheme_id == conceptscheme.id) \
                    .filter(ConceptModel.concept_id == int(mc)) \
                    .one()
                cm.members.add(mc)


def _check_language(language_tag, session):
    '''
    Checks if a certain language is already present, if not import.

    :param string language_tag: IANA language tag
    :param session: Database session to use
    :rtype: :class:`skosprovider_sqlalchemy.models.Language`
    '''
    if not language_tag:
        language_tag = 'und'
    l = session.query(LanguageModel).get(language_tag)
    if not l:
        if not tags.check(language_tag):
            raise ValueError('Unable to import provider. Invalid language tag: %s' % language_tag)
        descriptions = ', '.join(tags.description(language_tag))
        l = LanguageModel(id=language_tag, name=descriptions)
        session.add(l)
    return l

def _add_labels(target, labels, session):
    '''
    Adds the labels to the target

    :param target: Target to add the labels to
    :param labels: A list of :class:`skosprovider.skos.Label` instances.
    :param session:  A :class:`sqlalchemy.orm.session.Session`.
    '''
    for l in labels:
        _check_language(l.language, session)
        target.labels.append(LabelModel(
            label=l.label,
            labeltype_id=l.type,
            language_id=l.language
        ))
    return target

def _add_notes(target, notes, session):
    '''
    Adds the notes to the target

    :param target: Target to add the notes to
    :param notes: A list of :class:`skosprovider.skos.Note` instances.
    :param session:  A :class:`sqlalchemy.orm.session.Session`.
    '''
    for n in notes:
        _check_language(n.language, session)
        target.notes.append(NoteModel(
            note=n.note,
            notetype_id=n.type,
            language_id=n.language,
            markup=n.markup
        ))
    return target

def _add_sources(target, sources, session):
    '''
    Adds the sources to the target

    :param target: Target to add the sources to
    :param sources: A list of :class:`skosprovider.skos.Source` instances.
    :param session:  A :class:`sqlalchemy.orm.session.Session`.
    '''
    for s in sources:
        target.sources.append(SourceModel(
            citation=s.citation,
            markup=s.markup
        ))
    return target

class VisitationCalculator(object):
    '''
    Generates a nested set for a conceptscheme.
    '''

    def __init__(self, session):
        '''
        :param :class:`sqlalchemy.orm.session.Session` session: A database
            session.
        '''
        self.session = session

    def visit(self, conceptscheme):
        '''
        Visit a :class:`skosprovider_sqlalchemy.models.Conceptscheme` and
        calculate a nested set representation.

        :param conceptscheme: A
            :class:`skosprovider_sqlalchemy.models.Conceptscheme` for which
            the nested set will be calculated.
        '''
        self.count = 0
        self.depth = 0
        self.visitation = []
        topc = self.session \
            .query(ConceptModel) \
            .filter(ConceptModel.conceptscheme == conceptscheme) \
            .filter(ConceptModel.broader_concepts == None) \
            .all()
        for tc in topc:
            self._visit_concept(tc)
        self.visitation.sort(key=lambda v: v['lft'])
        return self.visitation

    def _visit_concept(self, concept):
        log.debug('Visiting concept %s.' % concept.id)
        self.depth += 1
        self.count += 1
        v = {
            'id': concept.id,
            'lft': self.count,
            'depth': self.depth
        }
        if concept.type == 'concept':
            for nc in concept.narrower_concepts:
                self._visit_concept(nc)
        self.count += 1
        v['rght'] = self.count
        self.visitation.append(v)
        self.depth -= 1


def session_factory(session_maker_name):
    def with_session(fn):
        def go(parent_object, *args, **kw):
            if hasattr(parent_object, session_maker_name):
                root_call = True
                session_maker = getattr(parent_object, session_maker_name)
                if not hasattr(parent_object, 'session'):
                    parent_object.session = None
                if parent_object.session is None:
                    session = session_maker()
                    parent_object.session = session
                else:
                    root_call = False
                try:
                    parent_object.session.begin(subtransactions=True)
                    ret = fn(parent_object, *args, **kw)
                    parent_object.session.commit()
                    return ret
                except:
                    parent_object.session.rollback()
                    raise
                finally:
                    if root_call:
                        parent_object.session.close()
                        parent_object.session = None
            else:
                raise Exception('session_maker %s not found' % session_maker_name)

        return go
    return with_session
