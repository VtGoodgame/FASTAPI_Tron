import logging
from uuid import UUID
from fastapi import Request
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src import concts as c

