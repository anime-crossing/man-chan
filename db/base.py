from sqlalchemy import Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column

from .connection import session

_Base = declarative_base()


class Base(_Base):
    __tablename__ = "base"

    id = Column(Integer, autoincrement=True, primary_key=True)

    session = session
