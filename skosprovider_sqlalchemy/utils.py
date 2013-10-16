# -*- coding: utf-8 -*-

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
                cm = session.query(ConceptModel).get(int(c.id))
                for nc in c.narrower:
                    nc = session.query(ConceptModel).get(int(nc))
                    cm.narrower_concepts.append(nc)
            if len(c.related) > 0:
                cm = session.query(ConceptModel).get(int(c.id))
                for rc in c.related:
                    rc = session.query(ConceptModel).get(int(rc))
                    cm.related_concepts.add(rc)
        elif isinstance(c, Collection) and len(c.members) > 0:
            cm = session.query(CollectionModel).get(int(c.id))
            for mc in c.members:
                mc = session.query(ThingModel).get(int(mc))
                cm.members.append(mc)
