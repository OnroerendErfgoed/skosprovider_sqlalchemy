import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import ConceptScheme
from ..models import Visitation
from ..utils import VisitationCalculator



def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <connect_uri> <concept_scheme_id>\n'
          '(example: "%s sqlite:///skos.db 1")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 3:
        usage(argv)
    connect_uri = argv[1]
    scheme_id = argv[2]
    engine = create_engine(connect_uri)
    session = sessionmaker(
        bind=engine,
    )()
    vc = VisitationCalculator(session)
    cs = session.get(ConceptScheme, scheme_id)
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
    session.commit()
