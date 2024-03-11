from typing import Any, Dict, List

from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, Session
from sqlalchemy.schema import Column

from .connection import get_session


class Base(object):
    id = Column(Integer, autoincrement=True, primary_key=True)

    def __init__(self, **kwargs: Any):
        ...

    @classmethod
    @property
    def _session(cls) -> Session:
        return get_session()

    @classmethod
    def _create(cls, **kwargs: Any):
        base = cls(**kwargs)
        session = cls._session

        try:
            session.add(base)
            session.commit()
        except:
            session.rollback()

        return base

    @classmethod
    def _query(cls, entities: List[Any] = []) -> "Query[Any]":
        """
        Creates a query object from session.

        Use case:
        Class._query(entities=[Class.id, Class.name]).all()

        Returns:
        [(Class.id, Class.name), ...]
        """
        if not entities:
            entities = [cls]

        return cls._session.query(*entities)

    @classmethod
    def _list(cls, **filter: Dict[str, Any]):
        """
        Gives a list of objects from a certain table filtered.

        Use case:
        Class._list(id=2, name="test)

        Returns:
        [Class, Class, ...]
        """
        return cls._session.query(cls).filter_by(**filter).all()

    def _save(self):
        session = self._session

        try:
            session.commit()
        except:
            session.rollback()


Base = declarative_base(cls=Base)
