from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    picture = Column(String)
    provider = Column(String, nullable=False)  # google, github, etc.
    provider_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
