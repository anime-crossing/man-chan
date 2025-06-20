from typing import Optional, cast

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker


class DatabaseException(Exception):
    pass


class SessionContainer:
    session: Optional[Session] = None
    engine: Optional[Engine] = None
    plugin_session: Optional[Session] = None
    plugin_engine: Optional[Engine] = None


def setup_db_session(database: str) -> bool:
    """Call this at the beginning of the program."""
    engine = create_engine(database)
    session_maker = scoped_session(sessionmaker(bind=engine))
    SessionContainer.session = session_maker
    SessionContainer.engine = engine
    return True


def setup_plugins_db(database: str) -> bool:
    """Call this at the beginning of the program."""
    engine = create_engine(database)
    session_maker = scoped_session(sessionmaker(bind=engine))
    SessionContainer.plugin_session = session_maker
    SessionContainer.plugin_engine = engine
    return True


def get_session() -> Session:
    return cast(Session, SessionContainer.session)


def get_engine() -> Engine:
    return cast(Engine, SessionContainer.engine)
