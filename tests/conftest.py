import os
from pathlib import Path

import pytest
import pytest_asyncio
from starlette.testclient import TestClient

from config import Config
from dao import DAO
from endpoints.utils import get_dao
from main import app

if os.getcwd().endswith("/tests/"):
  conf_path = Path("config/t_config.toml")
else:
  conf_path = Path(os.getcwd(), "tests/config/t_config.toml")
test_config = Config(conf_path)


@pytest.fixture(scope="session")
def config() -> Config:
  return test_config


@pytest.fixture(autouse=True)
def prepare_tables():
  DAO(test_config).init_tables()


@pytest.fixture(autouse=True)
def prepare_app(config: Config):
  app.state.config = config


@pytest.fixture()
def client() -> TestClient:
  return TestClient(app)

