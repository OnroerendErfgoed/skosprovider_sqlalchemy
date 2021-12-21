import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import Base
from ..models import Initialiser


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <connect_uri>\n'
          '(example: "%s sqlite:///skos.db")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    connect_uri = argv[1]
    engine = create_engine(connect_uri)
    session = sessionmaker(
        bind=engine,
    )()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    init = Initialiser(session)
    init.init_all()
    session.commit()
