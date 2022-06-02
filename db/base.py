from sqlalchemy import Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, Query
from sqlalchemy.schema import Column

from .connection import get_session
from typing import List, Type, TypeVar, Any


class Base(object):

    id = Column(Integer, autoincrement=True, primary_key=True)

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

        try:
            session.add(base)
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

    @classmethod
    def _query(cls, entities = []) -> Query:
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
    def _list(cls, **filter):
        # type: (Type[TQuery], Any) -> List[TQuery]
        """
        Gives a list of objects from a certain table filtered.

        Use case:
        Class._list(id=2, name="test)

        Returns:
        [Class, Class, ...]
        """
        return cls._session.query(cls).filter_by(**filter).all()

Base = declarative_base(cls=Base)  # type: ignore
TQuery = TypeVar("TQuery", bound=Base)
