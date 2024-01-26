import os
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from starlette.testclient import TestClient

from config import Config
from db import DAO
from endpoints.utils import get_dao
from main import app
from tests.utils import create_tables, drop_all_tables

engine = create_async_engine('sqlite+aiosqlite:///:memory:')
testing_sessionmaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


@pytest.fixture(scope="session")
def config() -> Config:
    if os.getcwd().endswith("/tests/"):
        conf_path = Path("config/t_config.toml")
    else:
        conf_path = Path(os.getcwd(), "tests/config/t_config.toml")
    return Config(conf_path)


@pytest_asyncio.fixture(autouse=True)
async def prepare_tables():
    try:
        await create_tables(engine)
        yield
    finally:
        await drop_all_tables(engine)


@pytest.fixture(autouse=True)
def prepare_app(config: Config):
    app.state.config = config
    app.dependency_overrides[get_dao] = override_get_dao


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


async def override_get_dao() -> DAO:
    session = testing_sessionmaker()
    try:
        yield DAO(session)
    finally:
        await session.commit()
        await session.close()
