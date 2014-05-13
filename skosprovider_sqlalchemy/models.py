# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    ForeignKey,
    UniqueConstraint,
    Table,
    event
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    relationship,
    backref
)

Base = declarative_base()

concept_label = Table(
    'concept_label',
    Base.metadata,
    Column('concept_id', Integer, ForeignKey('concept.id'), primary_key=True),
    Column('label_id', Integer, ForeignKey('label.id'), primary_key=True)
)

conceptscheme_label = Table(
    'conceptscheme_label',
    Base.metadata,
    Column(
        'conceptscheme_id',
        Integer,
        ForeignKey('conceptscheme.id'),
        primary_key=True
    ),
    Column('label_id', Integer, ForeignKey('label.id'), primary_key=True)
)

concept_note = Table(
    'concept_note',
    Base.metadata,
    Column('concept_id', Integer, ForeignKey('concept.id'), primary_key=True),
    Column('note_id', Integer, ForeignKey('note.id'), primary_key=True)
)

conceptscheme_note = Table(
    'conceptscheme_note',
    Base.metadata,
    Column(
        'conceptscheme_id',
        Integer,
        ForeignKey('conceptscheme.id'),
        primary_key=True
    ),
    Column('note_id', Integer, ForeignKey('note.id'), primary_key=True)
)

collection_concept = Table(
    'collection_concept',
    Base.metadata,
    Column(
        'collection_id',
        Integer,
        ForeignKey('concept.id'),
        primary_key=True
    ),
    Column('concept_id', Integer, ForeignKey('concept.id'), primary_key=True)
)

concept_related_concept = Table(
    'concept_related_concept',
    Base.metadata,
    Column(
        'concept_id_from',
        Integer,
        ForeignKey('concept.id'),
        primary_key=True
    ),
    Column(
        'concept_id_to',
        Integer,
        ForeignKey('concept.id'),
        primary_key=True
    )
)

concept_hierarchy_concept = Table(
    'concept_hierarchy_concept',
    Base.metadata,
    Column(
        'concept_id_broader',
        Integer,
        ForeignKey('concept.id'),
        primary_key=True
    ),
    Column(
        'concept_id_narrower',
        Integer,
        ForeignKey('concept.id'),
        primary_key=True
    )
)

concept_hierarchy_collection = Table(
    'concept_hierarchy_collection',
    Base.metadata,
    Column(
        'concept_id_broader',
        Integer,
        ForeignKey('concept.id'),
        primary_key=True
    ),
    Column(
        'collection_id_narrower',
        Integer,
        ForeignKey('concept.id'),
        primary_key=True
    )
)


class Thing(Base):
    '''
    Abstract class for both :class:`Concept` and :class:`Collection`.
    '''
    __tablename__ = 'concept'
    __table_args__ = (
        UniqueConstraint('conceptscheme_id', 'concept_id'),
    )
    id = Column(Integer, primary_key=True)
    type = Column(String(30))
    concept_id = Column(
        Integer,
        nullable=False,
        index=True
    )
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
    conceptscheme_id = Column(
        Integer,
        ForeignKey('conceptscheme.id'),
        nullable=False,
        index=True
    )


    def label(self, language='any'):
        return label(self.labels, language)

    __mapper_args__ = {
        'polymorphic_on': 'type',
        'polymorphic_identity': 'thing'
    }


class Concept(Thing):
    '''
    A concept as know by :term:`skosprovider:SKOS`.
    '''

    related_concepts = relationship(
        'Concept',
        secondary=concept_related_concept,
        primaryjoin='Concept.id==concept_related_concept.c.concept_id_to',
        secondaryjoin='Concept.id==concept_related_concept.c.concept_id_from',
        collection_class=set
    )

    narrower_concepts = relationship(
        'Concept',
        secondary=concept_hierarchy_concept,
        backref=backref('broader_concepts', collection_class=set),
        primaryjoin='Concept.id==concept_hierarchy_concept.c.concept_id_broader',
        secondaryjoin='Concept.id==concept_hierarchy_concept.c.concept_id_narrower',
        collection_class=set
    )

    narrower_collections = relationship(
        'Collection',
        secondary=concept_hierarchy_collection,
        backref=backref('broader_concepts', collection_class=set),
        primaryjoin='Concept.id==concept_hierarchy_collection.c.concept_id_broader',
        secondaryjoin='Concept.id==concept_hierarchy_collection.c.collection_id_narrower',
        collection_class=set
    )

    __mapper_args__ = {
        'polymorphic_identity': 'concept'
    }


def related_concepts_append_listener(target, value, initiator):
    '''
    Listener that ensures related concepts have a bidirectional
    relationship.
    '''

    if not hasattr(target, '__related_to_'):
        target.__related_to__ = set()

    target.__related_to__.add(value)

    if (target) not in getattr(value, '__related_to__', set()):
        value.related_concepts.add(target)

event.listen(
    Concept.related_concepts,
    'append',
    related_concepts_append_listener
)


def related_concepts_remove_listener(target, value, initiator):
    '''
    Listener to remove a related concept from both ends of the relationship.
    '''

    if (value) in getattr(target, '__related_to__', set()):
        target.__related_to__.remove(value)

    if not hasattr(target, '__removed_from__'):
        target.__removed_from__ = set()

    target.__removed_from__.add(value)

    if target in value.related_concepts and target not in getattr(value, '__removed_from__', set()):
            value.related_concepts.remove(target)

event.listen(Concept.related_concepts, 'remove', related_concepts_remove_listener)


class Collection(Thing):
    '''
    A collection as know by :term:`skosprovider:SKOS`.
    '''

    __mapper_args__ = {
        'polymorphic_identity': 'collection'
    }

    members = relationship(
        'Thing',
        secondary=collection_concept,
        backref=backref('member_of', collection_class=set),
        primaryjoin='Thing.id==collection_concept.c.collection_id',
        secondaryjoin='Thing.id==collection_concept.c.concept_id',
        collection_class=set
    )


class ConceptScheme(Base):
    '''
    A :term:`skosprovider:SKOS` conceptscheme.
    '''
    __tablename__ = 'conceptscheme'
    id = Column(Integer, primary_key=True)
    uri = Column(String(512))

    labels = relationship(
        'Label',
        secondary=conceptscheme_label,
        backref=backref('conceptscheme', uselist=False)
    )
    notes = relationship(
        'Note',
        secondary=conceptscheme_note,
        backref=backref('conceptscheme', uselist=False)
    )

    def label(self, language='any'):
        return label(self.labels, language)


class Language(Base):
    '''
    A Language.
    '''
    __tablename__ = 'language'
    id = Column(String(10), primary_key=True)
    name = Column(String(255))

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name


class LabelType(Base):
    '''
    A labelType according to :term:`skosprovider:SKOS`.
    '''
    __tablename__ = 'labeltype'
    name = Column(String(20), primary_key=True)
    description = Column(Text)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


class Label(Base):
    '''
    A label for a :class:`Concept`, :class:`Collection` or
    :class:`ConceptScheme`.
    '''
    __tablename__ = 'label'
    id = Column(Integer, primary_key=True)
    label = Column(
        String(512),
        nullable=False
    )

    labeltype = relationship('LabelType', uselist=False)
    language = relationship('Language', uselist=False)

    labeltype_id = Column(
        String(20),
        ForeignKey('labeltype.name'),
        nullable=False,
        index=True
    )
    language_id = Column(
        String(10),
        ForeignKey('language.id'),
        nullable=True,
        index=True
    )

    def __init__(self, label, labeltype_id='prefLabel', language_id=None):
        self.labeltype_id = labeltype_id
        self.language_id = language_id
        self.label = label

    def __str__(self):
        return self.label


class NoteType(Base):
    '''
    A noteType according to :term:`skosprovider:SKOS`.
    '''
    __tablename__ = 'notetype'

    name = Column(String(20), primary_key=True)
    description = Column(Text)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


class Note(Base):
    '''
    A note for a :class:`Concept`, :class:`Collection` or
    :class:`ConceptScheme`.
    '''
    __tablename__ = 'note'
    id = Column(Integer, primary_key=True)
    note = Column(
        Text,
        nullable=False
    )

    notetype = relationship('NoteType', uselist=False)
    notetype_id = Column(
        String(20),
        ForeignKey('notetype.name'),
        nullable=False,
        index=True
    )

    language = relationship('Language', uselist=False)
    language_id = Column(
        String(10),
        ForeignKey('language.id'),
        nullable=True,
        index=True
    )

    def __init__(self, note, notetype_id, language_id):
        self.notetype_id = notetype_id
        self.language_id = language_id
        self.note = note

    def __str__(self):
        return self.note


class Visitation(Base):
    '''
    Holds several nested sets.

    The visitation object and table hold several nested sets. Each
    :class:`skosprovider_sqlalchemy.models.Visitation` holds the positional
    information for one conceptplacement in a certain nested set.

    Each conceptscheme gets its own separate nested set.
    '''
    __tablename__ = 'visitation'
    id = Column(Integer, primary_key=True)
    lft = Column(Integer, index=True, nullable=False)
    rght = Column(Integer, index=True, nullable=False)
    depth = Column(Integer, index=True, nullable=False)

    conceptscheme = relationship('ConceptScheme')
    conceptscheme_id = Column(
        Integer,
        ForeignKey('conceptscheme.id'),
        nullable=False,
        index=True
    )
    concept = relationship('Concept')
    concept_id = Column(
        Integer,
        ForeignKey('concept.id'),
        nullable=False,
        index=True
    )


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

    Finally, if no label could be found, `None` is returned.

    :param list labels: A list of :class:`labels <Label>`.
    :param str language: The language for which a label should preferentially 
        be returned.
    :rtype: A :class:`Label` or `None` if no label could be found.
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
    '''
    Initialises a database.

    Adds necessary values for labelType, noteType and language to the database.

    The list of languages added by default is very small and will probably need
    to be expanded for your local needs.

    '''

    def __init__(self, session):
        self.session = session

    def init_all(self):
        '''
        Initialise all objects (labeltype, notetype, language).
        '''
        self.init_labeltype()
        self.init_notetype()
        self.init_languages()

    def init_notetype(self):
        '''
        Initialise the notetypes.
        '''
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
        '''
        Initialise the labeltypes.
        '''
        labeltypes = [
            ('hiddenLabel', 'A hidden label.'),
            ('altLabel', 'An alternative label.'),
            ('prefLabel', 'A preferred label.')
        ]
        for l in labeltypes:
            lt = LabelType(l[0], l[1])
            self.session.add(lt)

    def init_languages(self):
        '''
        Initialise the languages.

        Only adds a small set of languages. Will probably not be sufficient
        for most use cases.
        '''
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
