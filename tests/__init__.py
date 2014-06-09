# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


def _initTestingDB(engine):
    from skosprovider_sqlalchemy.models import (
        Base
    )
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(
        bind=engine
    )
    DBSession = Session()

    from skosprovider_sqlalchemy.models import (
        Initialiser
    )

    init = Initialiser(DBSession)
    init.init_all()
    return DBSession

engine = create_engine('sqlite:///:memory:', echo=True)


def setUpPackage():
    session = _initTestingDB(engine)
    session.commit()


def tearDownPackage():
    pass
