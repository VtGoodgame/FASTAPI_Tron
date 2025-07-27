from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src import consts as c

DATABASE_URL = c.DB_URL.format(
    DB_USER=c.DB_USER,
    DB_PASSWORD=c.DB_PASSWORD,
    DB_HOST=c.DB_HOST,
    DB_PORT=c.DB_PORT,
    DB_NAME=c.DB_NAME
)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
