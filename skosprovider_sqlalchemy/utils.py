# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from skosprovider.skos import (
    Concept,
    Collection
)

from skosprovider_sqlalchemy.models import (
    Thing as ThingModel,
    Concept as ConceptModel,
    Collection as CollectionModel,
    Label as LabelModel,
    Note as NoteModel
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

    # First pass: load all concepts and collections
    for stuff in provider.get_all():
        c = provider.get_by_id(stuff['id'])
        if isinstance(c, Concept):
            cm = ConceptModel(
                concept_id=int(c.id),
                uri=c.uri,
                conceptscheme=conceptscheme
            )
            for n in c.notes:
                cm.notes.append(NoteModel(
                    note=n.note,
                    notetype_id=n.type,
                    language_id=n.language
                ))
        elif isinstance(c, Collection):
            cm = CollectionModel(
                concept_id=int(c.id),
                uri=c.uri,
                conceptscheme=conceptscheme
            )
        for l in c.labels:
            cm.labels.append(LabelModel(
                label=l.label,
                labeltype_id=l.type,
                language_id=l.language
            ))
        session.add(cm)

    session.flush()

    # Second pass: link
    # Map for narrower concepts and collections
    modelmap = {
            'narrower_concepts': ConceptModel,
            'narrower_collections': CollectionModel
    }
    for stuff in provider.get_all():
        c = provider.get_by_id(stuff['id'])
        if isinstance(c, Concept):
            if len(c.narrower) > 0:
                cm = session.query(ConceptModel)\
                            .filter(ConceptModel.conceptscheme_id == conceptscheme.id)\
                            .filter(ConceptModel.concept_id == int(c.id))\
                            .one()
                for nc in c.narrower:
                    for narrow_model, Model in modelmap.items():
                        nc_query = session.query(Model) \
                            .filter(Model.conceptscheme_id == conceptscheme.id) \
                            .filter(Model.concept_id == int(nc))
                        if session.query(nc_query.exists()).one()[0]:
                            nc = nc_query.one()
                            getattr(cm, narrow_model).add(nc)
                            break
            if len(c.related) > 0:
                cm = session.query(ConceptModel)\
                            .filter(ConceptModel.conceptscheme_id == conceptscheme.id)\
                            .filter(ConceptModel.concept_id == int(c.id))\
                            .one()
                for rc in c.related:
                    rc = session.query(ConceptModel)\
                                .filter(ConceptModel.conceptscheme_id == conceptscheme.id)\
                                .filter(ConceptModel.concept_id == int(rc))\
                                .one()
                    cm.related_concepts.add(rc)
        elif isinstance(c, Collection) and len(c.members) > 0:
            cm = session.query(CollectionModel)\
                        .filter(ConceptModel.conceptscheme_id == conceptscheme.id)\
                        .filter(ConceptModel.concept_id == int(c.id))\
                        .one()
            for mc in c.members:
                mc = session.query(ThingModel)\
                            .filter(ConceptModel.conceptscheme_id == conceptscheme.id)\
                            .filter(ConceptModel.concept_id == int(mc))\
                            .one()
                cm.members.add(mc)


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
        topc = self.session\
                   .query(ConceptModel)\
                   .filter(ConceptModel.conceptscheme == conceptscheme)\
                   .filter(ConceptModel.broader_concepts == None)\
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
