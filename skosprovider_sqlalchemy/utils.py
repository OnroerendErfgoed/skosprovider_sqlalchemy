# -*- coding: utf-8 -*-

from skosprovider.skos import (
    Concept,
    Collection
)

from skosprovider_sqlalchemy.models import (
    Concept as ConceptModel,
    Collection as ColletionModel,
    Label as LabelModel,
    Note as NoteModel
)

def import_provider(provider, conceptscheme, session):

    for stuff in provider.get_all():
        c = provider.get_by_id(stuff['id'])
        #labels = [l.__dict__ for l in c.labels]
            
        if isinstance(c, Concept):
            cm = ConceptModel(
                id=c.id,
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
                id=c.id,
                conceptscheme=conceptscheme
            )
        for l in c.labels:
            cm.labels.append(LabelModel(
                label=l.label,
                labeltype_id=l.type,
                language_id=l.language
            ))
        session.add(cm)
