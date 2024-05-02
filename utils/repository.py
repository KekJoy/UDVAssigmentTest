import random
from typing import Annotated

from fastapi import Depends
from sqlalchemy import insert, select, update, or_, and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_maker, Base, get_async_session


class SQLAlchemyRepository:
    model: Base
    session: AsyncSession

    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_session)]):
        self.session = session

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def find_one(self, record_id: int):
        query = select(self.model).where(self.model.id == record_id)
        result = await self.session.execute(query)
        try:
            return result.scalar_one()
        except NoResultFound:
            return None

    async def update_one(self, record_id: int, data: dict):
        stmt = update(self.model).where(self.model.id == record_id).values(data)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def find_all(self, conditions: dict = None, OR=False, AND=False):
        query = select(self.model)

        if conditions:
            if OR:
                filters = []
                for key, value in conditions.items():
                    filters.append(getattr(self.model, key).__eq__(value))

                query = query.where(or_(*filters))
            elif AND:
                filters = []
                for key, value in conditions.items():
                    filters.append(getattr(self.model, key).__eq__(value))

                query = query.where(and_(*filters))
            else:
                for key, value in conditions.items():
                    query = query.where(getattr(self.model, key) == value)

        execute_result = await self.session.execute(query)
        data = execute_result.scalars().all()
        if not data:
            return None

        return data

    async def get_one(self, record_id: int):
        try:
            query = select(self.model).where(self.model.id == record_id)
            result = await self.session.execute(query)
            return result.scalar_one()
        except NoResultFound:
            return False
