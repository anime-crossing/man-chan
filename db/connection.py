from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

session = None


def create_db_connection():
    engine = create_engine("sqlite:///test_magi.db")
    session_maker = sessionmaker(bind=engine)

    global session
    session = session_maker()
