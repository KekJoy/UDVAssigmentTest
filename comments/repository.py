from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, select, func
from sqlalchemy.orm import mapped_column

from database import Base, async_session_maker
from utils.repository import SQLAlchemyRepository


class Comments(Base):
    __tablename__ = 'comments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    news_id = mapped_column(ForeignKey('News.id'), nullable=False)
    title = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    comment = Column(String, nullable=False)


class CommentsRepository(SQLAlchemyRepository):
    model = Comments

    async def comments_count(self, news_id: id):
        async with async_session_maker() as session:
            query = select(func.count()).select_from(self.model).where(self.model.news_id == news_id)
            result = await session.execute(query)
            return result.scalar()
