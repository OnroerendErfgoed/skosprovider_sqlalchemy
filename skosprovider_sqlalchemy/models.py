# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    ForeignKey,
    Table,
    event
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    relationship,
    backref
    )

Base = declarative_base()

concept_label = Table('concept_label', Base.metadata,
    Column('concept_id', Integer, ForeignKey('concept.id'), primary_key=True),
    Column('label_id', Integer, ForeignKey('label.id'), primary_key=True)
)

conceptscheme_label = Table('conceptscheme_label', Base.metadata,
    Column('conceptscheme_id', Integer, ForeignKey('conceptscheme.id'), primary_key=True),
    Column('label_id', Integer, ForeignKey('label.id'), primary_key=True)
)

concept_note = Table('concept_note', Base.metadata,
    Column('concept_id', Integer, ForeignKey('concept.id'), primary_key=True),
    Column('note_id', Integer, ForeignKey('note.id'), primary_key=True)
)

conceptscheme_note = Table('conceptscheme_note', Base.metadata,
    Column('conceptscheme_id', Integer, ForeignKey('conceptscheme.id'), primary_key=True),
    Column('note_id', Integer, ForeignKey('note.id'), primary_key=True)
)

collection_concept = Table('collection_concept', Base.metadata,
    Column('collection_id', Integer, ForeignKey('concept.id'), primary_key = True),
    Column('concept_id', Integer, ForeignKey('concept.id'), primary_key = True)
)

concept_related_concept = Table('concept_related_concept', Base.metadata,
    Column('concept_id_from', Integer, ForeignKey('concept.id'), primary_key=True),
    Column('concept_id_to', Integer, ForeignKey('concept.id'), primary_key=True)
)

concept_hierarchy_concept  = Table('concept_hierarchy_concept', Base.metadata,
    Column('concept_id_broader', Integer, ForeignKey('concept.id'), primary_key=True),
    Column('concept_id_narrower', Integer, ForeignKey('concept.id'), primary_key=True)
)


class Thing(Base):
    __tablename__ = 'concept'
    id = Column(Integer, primary_key=True)
    type = Column(String(30))
    uri = Column(String(512))
    labels = relationship(
        'Label', 
        secondary=concept_label, 
        backref=backref('concept', uselist=False),
        cascade='all, delete-orphan',
        single_parent=True
    )
    notes = relationship(
        'Note', 
        secondary=concept_note, 
        backref=backref('concept', uselist=False),
        cascade='all, delete-orphan',
        single_parent=True
    )

    conceptscheme = relationship('ConceptScheme', backref='concepts')
    conceptscheme_id = Column(Integer, ForeignKey('conceptscheme.id'))

    def label(self, language='any'):
        return label(self.labels, language)

    __mapper_args__ = {
        'polymorphic_on': 'type',
        'polymorphic_identity': 'thing'
    }


class Concept(Thing):

    related_concepts = relationship(
        'Concept', 
        secondary=concept_related_concept, 
        primaryjoin='Concept.id==concept_related_concept.c.concept_id_to',
        secondaryjoin='Concept.id==concept_related_concept.c.concept_id_from',
    )

    narrower_concepts = relationship(
        'Concept', 
        secondary=concept_hierarchy_concept,
        backref=backref('broader_concepts'),
        primaryjoin='Concept.id==concept_hierarchy_concept.c.concept_id_broader',
        secondaryjoin='Concept.id==concept_hierarchy_concept.c.concept_id_narrower',
    )

    __mapper_args__ = {
        'polymorphic_identity': 'concept'
    }


def related_concepts_append_listener(target, value, initiator):

    if not hasattr(target, '__related_to_'):
        target.__related_to__ = set()

    target.__related_to__.add(value)

    if (target) not in getattr(value, '__related_to__', set()):
        value.related_concepts.append(target)

event.listen(Concept.related_concepts, 'append', related_concepts_append_listener)


def related_concepts_remove_listener(target, value, initiator):

    if (value) in getattr(target, '__related_to__', set()):
        target.__related_to__.remove(value)

    if target in value.related_concepts:
        value.related_concepts.remove(target)

event.listen(Concept.related_concepts, 'remove', related_concepts_remove_listener)


class Collection(Thing):

    __mapper_args__ = {
        'polymorphic_identity': 'collection'
    }

    members = relationship(
        'Thing', 
        secondary=collection_concept, 
        backref=backref('collections'),
        primaryjoin='Thing.id==collection_concept.c.collection_id',
        secondaryjoin='Thing.id==collection_concept.c.concept_id'
    )


class ConceptScheme(Base):
    __tablename__ = 'conceptscheme'
    id = Column(Integer, primary_key=True)
    uri = Column(String(512))

    labels = relationship('Label', secondary=conceptscheme_label, backref=backref('conceptscheme', uselist=False))
    notes = relationship('Note', secondary=conceptscheme_note, backref=backref('conceptscheme', uselist=False))

    def label(self, language='any'):
        return label(self.labels, language)


class Language(Base):
    __tablename__ = 'language'
    id = Column(String(10), primary_key=True)
    name = Column(String(255))

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name


class LabelType(Base):
    __tablename__ = 'labeltype'
    
    name = Column(String(20), primary_key=True)
    description = Column(Text)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


class Label(Base):
    __tablename__ = 'label'
    id = Column(Integer, primary_key=True)
    label= Column(String(512))

    labeltype = relationship('LabelType', uselist = False)
    language = relationship('Language', uselist = False)

    labeltype_id = Column(String(20), ForeignKey('labeltype.name')) 
    language_id = Column(String(10), ForeignKey('language.id'), nullable=True)

    def __init__(self, label, labeltype_id = 'prefLabel', language_id = None):
        self.labeltype_id = labeltype_id
        self.language_id = language_id
        self.label = label

    def __str__(self):
        return self.label


class NoteType(Base):
    __tablename__ = 'notetype'
    
    name = Column(String(20), primary_key=True)
    description = Column(Text)

    def __init__(self, name, description):
        
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


class Note(Base):
    __tablename__ = 'note'
    id = Column(Integer, primary_key=True)
    note = Column(Text)

    notetype = relationship('NoteType', uselist = False)
    notetype_id = Column(String(20), ForeignKey('notetype.name'))

    language = relationship('Language', uselist = False)
    language_id = Column(String(10), ForeignKey('language.id'), nullable=True)

    def __init__(self, notetype_id, language_id, note):
        self.notetype_id = notetype_id
        self.language_id = language_id
        self.note = note


def label(labels=[], language='any'):
    '''
    Provide a label for a list of labels.

    The items in the list of labels are assumed to be instances of
    :class:`Label`.

    This method tries to find a label by looking if there's
    a pref label for the specified language. If there's no pref label,
    it looks for an alt label. It disregards hidden labels.

    If language 'any' was specified, all labels will be considered,
    regardless of language.

    To find a label without a specified language, pass `None` as language.

    If a language or None was specified, and no label could be found, this
    method will automatically try to find a label in some other language.

    Finally, if no label could be found, None is returned.
    '''
    alt = None
    for l in labels:
        if language == 'any' or l.language_id == language:
            labeltype = l.labeltype_id or l.labeltype.name
            if labeltype == 'prefLabel':
                return l
            if alt is None and labeltype == 'altLabel':
                alt = l
    if alt is not None:
        return alt
    elif language != 'any':
        return label(labels, 'any')
    else:
        return None


class Initialiser(object):

    def __init__(self, session):
        self.session = session

    def init_all(self):
        self.init_labeltype()
        self.init_notetype()
        self.init_languages()

    def init_notetype(self):
        notetypes = [
            ('changeNote', 'A change note.'),
            ('definition', 'A definition.'),
            ('editorialNote', 'An editorial note.'),
            ('example', 'An example.'),
            ('historyNote', 'A historynote.'),
            ('scopeNote', 'A scopenote.'),
            ('note', 'A note.')
        ]
        for n in notetypes:
            nt = NoteType(n[0], n[1])
            self.session.add(nt)

    def init_labeltype(self):
        labeltypes = [
            ('hiddenLabel', 'A hidden label.'),
            ('altLabel', 'An alternative label.'),
            ('prefLabel', 'A preferred label.')
        ]
        for l in labeltypes:
            lt = LabelType(l[0], l[1])
            self.session.add(lt)

    def init_languages(self):
        languages = [
            ('la', 'Latin'),
            ('nl', 'Dutch'),
            ('vls', 'Flemish'),
            ('en', 'English'),
            ('fr', 'French'),
            ('de', 'German')
        ]
        for l in languages:
            lan = Language(l[0], l[1])
            self.session.add(lan)
