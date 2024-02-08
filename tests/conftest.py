import pytest
from starlette.testclient import TestClient

from main import app
from src.config import Config
from src.dao import get_conn, setup_db


@pytest.fixture()
def config(tmp_path) -> Config:
  return Config(
    id_len=5,
    base_url="http://127.0.0.1:8000",
    db_name=tmp_path / "testdb.sqlite"
  )


@pytest.fixture(autouse=True)
def prepare_tables(config: Config):
  with get_conn(config.db_name) as conn:
    setup_db(conn)


@pytest.fixture(autouse=True)
def prepare_app(config: Config):
  app.state.config = config


@pytest.fixture()
def client() -> TestClient:
  return TestClient(app)


