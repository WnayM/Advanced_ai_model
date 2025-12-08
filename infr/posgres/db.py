from __future__ import annotations
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")

class Base(DeclarativeBase):
    pass

engine = create_engine(
    DATABASE_URL,
    echo = False,
    pool_pre_ping = True
)

SessionLocal = sessionmaker(
    bind = engine,
    autoflush = False,
    autocommit = False
)