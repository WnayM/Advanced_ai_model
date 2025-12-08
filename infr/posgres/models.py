from sqlalchemy import Column, SmallInteger, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from db import Base

class User(Base) :
    __tablename__ = "users"

    id = Column(BigInteger, primary_key = True, index = True, autoincrement = True)
    external_id = Column(String, unique = True, nullable = False)
    created_at = Column(DateTime(timezone = True), nullable = False, server_default = func.now())

class articles(Base) :
    __tablename__ = "articles"
    id = Column(BigInteger, primary_key = True, index = True)
    url = Column(String, unique = True, nullable = False)
    title = Column(String, nullable = False)
    content = Column(String)
    source = Column(String, nullable = False)
    language = Column(String(20))
    published_at = Column(DateTime(timezone = True), nullable = True, server_default = func.now())
    created_at = Column(DateTime(timezone=False), nullable = False, server_default=func.now())

class user_events(Base) :
    __tablename__ = "user_events"
    id = Column(BigInteger, primary_key=True, index= True, autoincrement = True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable = False)
    article_id = Column(BigInteger, ForeignKey("articles.id", ondelete = "CASCADE"), nullable = False)
    event_type = Column(String(32), nullable = False)
    event_value = Column(SmallInteger)
    event_ts = Column(DateTime(timezone=True), nullable = False, server_default = func.now())
