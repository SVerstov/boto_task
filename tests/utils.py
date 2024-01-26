from db.base import Base


async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
