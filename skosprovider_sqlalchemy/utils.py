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

    #First pass: load all concepts and collections
    for stuff in provider.get_all():
        c = provider.get_by_id(stuff['id'])
        if isinstance(c, Concept):
            cm = ConceptModel(
                id=int(c.id),
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
                id=int(c.id),
                conceptscheme=conceptscheme
            )
        for l in c.labels:
            cm.labels.append(LabelModel(
                label=l.label,
                labeltype_id=l.type,
                language_id=l.language
            ))
        session.add(cm)

    #Second pass: link
    for stuff in provider.get_all():
        c = provider.get_by_id(stuff['id'])
        if isinstance(c, Concept): 
            if len(c.narrower) > 0:
                cm = session.query(ConceptModel)\
                            .get((int(c.id), conceptscheme.id))
                for nc in c.narrower:
                    nc = session.query(ConceptModel)\
                                .get((int(nc), conceptscheme.id))
                    cm.narrower_concepts.add(nc)
            if len(c.related) > 0:
                cm = session.query(ConceptModel)\
                            .get((int(c.id), conceptscheme.id))
                for rc in c.related:
                    rc = session.query(ConceptModel)\
                                .get((int(rc), conceptscheme.id))
                    cm.related_concepts.add(rc)
        elif isinstance(c, Collection) and len(c.members) > 0:
            cm = session.query(CollectionModel)\
                        .get((int(c.id), conceptscheme.id))
            for mc in c.members:
                mc = session.query(ThingModel)\
                            .get((int(mc), conceptscheme.id))
                cm.members.add(mc)

class VisitationCalculator(object):

    def __init__(self, session):
        self.session = session

    def visit(self, conceptscheme):
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
