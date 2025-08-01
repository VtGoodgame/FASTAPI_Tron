# src/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from src import consts as c

# Определяем Base до модели
Base = declarative_base()

# Проверяем, мы в режиме  тестирования
TESTING = os.getenv("TESTING", "False").lower() == "true"

if TESTING:
    DATABASE_URL = "sqlite:///./test.db"
else:
    # Формируем DATABASE_URL из констант
    DATABASE_URL = c.DB_URL.format(
        DB_USER=c.DB_USER,
        DB_PASSWORD=c.DB_PASSWORD,
        DB_HOST=c.DB_HOST,
        DB_PORT=c.DB_PORT,
        DB_NAME=c.DB_NAME
    )

# Создаём engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Создаём сессию
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Зависимость для получения сессии SQLAlchemy.
    Используется в FastAPI через Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создаём таблицы 
def create_tables():
    Base.metadata.create_all(bind=engine)