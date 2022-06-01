from sqlalchemy import Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.schema import Column

from .connection import get_session


class Base(object):

    id = Column(Integer, autoincrement=True, primary_key=True)
    temp = Column(String, nullable=True)

    def __init__(self, **kwargs):
        ...

    @classmethod
    @property
    def _session(cls) -> Session:
        return get_session()

    @classmethod
    def _create(cls, **kwargs):
        base = cls(**kwargs)
        session = cls._session

        session.add(base)
        session.commit()
        session.close()

    @classmethod
    def list(cls):
        print("TYPE", type(cls))
        return cls._session.query(cls).all()


Base = declarative_base(cls=Base)  # type: ignore


class Child(Base):
    __tablename__ = "child"

    col = Column(String, nullable=True)

    @classmethod
    def create(cls, col=""):
        cls._create(**{"col": col, "temp": "invalid"})
