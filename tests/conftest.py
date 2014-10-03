import pytest

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from skosprovider_sqlalchemy.models import (
    Base,
    Initialiser
)

from skosprovider_sqlalchemy.providers import (
    SQLAlchemyProvider
)

def pytest_addoption(parser):
    parser.addoption(
        '--sqlalchemy_url',
        action='store',
        default='sqlite:///:memory:',
        help='SQLAlchemy connection url to database under test.'
    )

@pytest.fixture(scope='session')
def engine(request):
    engine = create_engine(
        request.config.getoption('--sqlalchemy_url'),
        echo=True
    )
    Base.metadata.create_all(engine)

    def finalize():
        Base.metadata.drop_all(engine)

    request.addfinalizer(finalize)
    return engine

@pytest.fixture()
def session(request, engine):
    connection = engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(
        bind=engine
    )
    DBSession = Session()

    init = Initialiser(DBSession)
    init.init_all()

    def finalize():
        DBSession.close()
        transaction.rollback()

    request.addfinalizer(finalize)
    return DBSession

@pytest.fixture()
def provider(request, test_data, session):
    from skosprovider.uri import UriPatternGenerator
    provider = SQLAlchemyProvider(
        {'id': 'SOORTEN', 'conceptscheme_id': 1},
        session,
        uri_generator=UriPatternGenerator('urn:x-skosprovider-sa:test:%s')
    )
    return provider

@pytest.fixture()
def test_data(request, session):
    from skosprovider_sqlalchemy.models import (
        Concept,
        ConceptScheme,
        Collection,
        Label,
        Note
    )
    cs = ConceptScheme(
        id=1,
        uri='urn:x-skosprovider:test'
    )
    session.add(cs)
    con = Concept(
        id=10,
        uri='urn:x-skosprovider:test:1',
        concept_id=1,
        conceptscheme=cs
    )
    session.add(con)
    l = Label('Churches', 'prefLabel', 'en')
    con.labels.append(l)
    l = Label('Kerken', 'prefLabel', 'nl')
    con.labels.append(l)
    col = Collection(
        id=20,
        uri='urn:x-skosprovider:test:2',
        concept_id=2,
        conceptscheme=cs
    )
    col.broader_concepts.add(con)
    l = Label('Churches by function', 'prefLabel', 'en')
    col.labels.append(l)
    session.add(col)
    chap = Concept(
        id=30,
        uri='urn:x-skosprovider:test:3',
        concept_id=3,
        conceptscheme=cs
    )
    l = Label('Chapels', 'prefLabel', 'en')
    chap.labels.append(l)
    session.add(chap)
    chap.related_concepts.add(con)
    tchap = Concept(
        id=50,
        uri='urn:x-skosprovider:test:5',
        concept_id=5,
        conceptscheme=cs
    )
    tchap.labels.append(Label('Boomkapellen', 'prefLabel', 'nl'))
    session.add(tchap)
    tchap.broader_concepts.add(chap)
    cath = Concept(
        id=40,
        uri='urn:x-skosprovider:test:4',
        concept_id=4,
        conceptscheme=cs
    )
    l = Label('Cathedrals', 'prefLabel', 'en')
    cath.labels.append(l)
    n = Note(
        'A cathedral is a church which contains the seat of a bishop.',
        'definition',
        'en'
    )
    cath.notes.append(n)
    session.add(cath)
    cath.broader_concepts.add(con)
    cath.member_of.add(col)

@pytest.fixture()
def visitationprovider(request, test_data, session):
    provider = SQLAlchemyProvider(
        {'id': 'SOORTEN', 'conceptscheme_id': 1},
        session,
        expand_strategy='visit'
    )
    return provider

@pytest.fixture()
def create_visitation(session, test_data):
    from skosprovider_sqlalchemy.utils import (
        VisitationCalculator
    )
    from skosprovider_sqlalchemy.models import (
        Visitation,
        ConceptScheme
    )
    vc = VisitationCalculator(session)
    conceptschemes = session.query(ConceptScheme).all()
    for cs in conceptschemes:                     
        visit = vc.visit(cs)
        for v in visit:
            vrow = Visitation(
                conceptscheme=cs,
                concept_id=v['id'],
                lft=v['lft'],
                rght=v['rght'],
                depth=v['depth']
            )
            session.add(vrow)
