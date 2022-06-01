from typing import Optional, cast

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker


class SessionContainer:
    session: Optional[Session] = None
    engine: Optional[Engine] = None


def setup_db_session():
    """Call this at the beginning of the program."""
    engine = create_engine("sqlite:///test_magi.db")
    session_maker = scoped_session(sessionmaker(bind=engine))
    SessionContainer.session = session_maker
    SessionContainer.engine = engine


def get_session() -> Session:
    return cast(Session, SessionContainer.session)


def get_engine() -> Engine:
    return cast(Engine, SessionContainer.engine)
