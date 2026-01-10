from sqlalchemy import Column, SmallInteger, String, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    external_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Article(Base):
    __tablename__ = "articles"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text)
    source = Column(String, nullable=False)
    language = Column(String(20))
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(BigInteger, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(32), nullable=False)  # "like" | "dislike"
    event_value = Column(SmallInteger)               # 1
    event_ts = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
