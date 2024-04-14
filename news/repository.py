from sqlalchemy import Column, Integer, String, DateTime, Boolean

from database import Base
from utils.repository import SQLAlchemyRepository


class News(Base):
    __tablename__ = 'News'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    body = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)


class NewsRepository(SQLAlchemyRepository):
    model = News
