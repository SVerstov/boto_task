import pytest
from starlette.testclient import TestClient

from src.config import Config
from main import app
from src.dao import setup_db, get_conn


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


