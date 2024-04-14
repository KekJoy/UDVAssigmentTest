from sqlalchemy import insert, select, update, or_, and_
from sqlalchemy.exc import NoResultFound

from database import async_session_maker


class SQLAlchemyRepository:
    model = None

    async def add_one(self, data: dict):
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()

    async def find_one(self, record_id: int):
        async with async_session_maker() as session:
            query = select(self.model).where(self.model.id == record_id)
            result = await session.execute(query)
            try:
                return result.scalar_one()
            except NoResultFound:
                return None

    async def update_one(self, record_id: int, data: dict):
        async with async_session_maker() as session:
            stmt = update(self.model).where(self.model.id == record_id).values(data)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount

    async def find_all(self, conditions: dict = None, OR=False, AND=False):
        async with async_session_maker() as session:
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

            execute_result = await session.execute(query)
            data = execute_result.scalars().all()
            if not data:
                return None

            return data

    async def get_one(self, record_id: int):
        async with async_session_maker() as session:
            try:
                query = select(self.model).where(self.model.id == record_id)
                result = await session.execute(query)
                return result.scalar_one()
            except NoResultFound:
                return False
