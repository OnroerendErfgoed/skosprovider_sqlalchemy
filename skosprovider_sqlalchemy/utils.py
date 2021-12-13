import logging

from language_tags import tags
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from sqlalchemy.orm.exc import NoResultFound

from skosprovider_sqlalchemy.models import Collection as CollectionModel
from skosprovider_sqlalchemy.models import Concept as ConceptModel
from skosprovider_sqlalchemy.models import Label as LabelModel
from skosprovider_sqlalchemy.models import Language as LanguageModel
from skosprovider_sqlalchemy.models import Match as MatchModel
from skosprovider_sqlalchemy.models import Note as NoteModel
from skosprovider_sqlalchemy.models import Source as SourceModel
from skosprovider_sqlalchemy.models import Thing as ThingModel

log = logging.getLogger(__name__)


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
                    try:
                        nc = session.query(ConceptModel) \
                            .filter(ConceptModel.conceptscheme_id == conceptscheme.id) \
                            .filter(ConceptModel.concept_id == int(nc)) \
                            .one()
                        cm.narrower_concepts.add(nc)
                    except NoResultFound:
                        log.warning(
                            'Tried to add a relation %s narrower %s, but target \
                            does not exist. Relation will be lost.' % (c.id, nc))
            if len(c.subordinate_arrays) > 0:
                for sa in c.subordinate_arrays:
                    try:
                        sa = session.query(CollectionModel) \
                            .filter(CollectionModel.conceptscheme_id == conceptscheme.id) \
                            .filter(CollectionModel.concept_id == int(sa)) \
                            .one()
                        cm.narrower_collections.add(sa)
                    except NoResultFound:
                        log.warning(
                            'Tried to add a relation %s subordinate array %s, but target \
                            does not exist. Relation will be lost.' % (c.id, sa))
            if len(c.related) > 0:
                for rc in c.related:
                    try:
                        rc = session.query(ConceptModel) \
                            .filter(ConceptModel.conceptscheme_id == conceptscheme.id) \
                            .filter(ConceptModel.concept_id == int(rc)) \
                            .one()
                        cm.related_concepts.add(rc)
                    except NoResultFound:
                        log.warning(
                            'Tried to add a relation %s related %s, but target \
                            does not exist. Relation will be lost.' % (c.id, rc))
        elif isinstance(c, Collection) and len(c.members) > 0:
            cm = session.query(CollectionModel) \
                .filter(ConceptModel.conceptscheme_id == conceptscheme.id) \
                .filter(ConceptModel.concept_id == int(c.id)) \
                .one()
            for mc in c.members:
                try:
                    mc = session.query(ThingModel) \
                        .filter(ConceptModel.conceptscheme_id == conceptscheme.id) \
                        .filter(ConceptModel.concept_id == int(mc)) \
                        .one()
                    cm.members.add(mc)
                except NoResultFound:
                    log.warning(
                        'Tried to add a relation %s member %s, but target \
                        does not exist. Relation will be lost.' % (c.id, mc))


def _check_language(language_tag, session):
    '''
    Checks if a certain language is already present, if not import.

    :param string language_tag: IANA language tag
    :param session: Database session to use
    :rtype: :class:`skosprovider_sqlalchemy.models.Language`
    '''
    if not language_tag: # pragma: no cover
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

class VisitationCalculator:
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
        # get all possible top concepts
        topc = self.session \
            .query(ConceptModel) \
            .filter(ConceptModel.conceptscheme == conceptscheme) \
            .filter(ConceptModel.broader_concepts == None) \
            .all()
        # check if they have an indirect broader concept
        def _has_higher_concept(c):
            for coll in c.member_of:
                if coll.infer_concept_relations and (coll.broader_concepts or _has_higher_concept(coll)):
                    return True
            return False
        topc = [c for c in topc if not _has_higher_concept(c)]
        for tc in topc:
            self._visit_concept(tc)
        self.visitation.sort(key=lambda v: v['lft'])
        return self.visitation

    def _visit_concept(self, concept):
        if concept.type == 'concept':
            log.debug('Visiting concept %s.' % concept.id)
            self.depth += 1
            self.count += 1
            v = {
                'id': concept.id,
                'lft': self.count,
                'depth': self.depth
            }
            for nc in concept.narrower_concepts:
                self._visit_concept(nc)
            for ncol in concept.narrower_collections:
                if ncol.infer_concept_relations:
                    self._visit_concept(ncol)
            self.count += 1
            v['rght'] = self.count
            self.visitation.append(v)
            self.depth -= 1
        elif concept.type == 'collection':
            log.debug('Visiting collection %s.' % concept.id)
            for m in concept.members:
                self._visit_concept(m)
