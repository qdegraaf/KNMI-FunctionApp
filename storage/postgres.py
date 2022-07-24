from requests import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_psql_session(
    username: str,
    password: str,
    host: str,
    port: int = 5432,
) -> Session:
    """
    Return Postgres session for given connection credentials.
    """
    connect_str = f"postgresql://{username}:{password}@{host}:{port}"
    engine = create_engine(connect_str)
    db_session = sessionmaker(bind=engine)
    return db_session()
