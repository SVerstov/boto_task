import sqlite3
from datetime import datetime

from pathlib import Path

from config import Config
from dao.base import BaseDAO
from dao.links_dao import LinkDAO


def _adapt_datetime(dt: datetime):
  return dt.isoformat()


def _convert_datetime_int(dt_bytes: bytes):
  return datetime.fromisoformat(dt_bytes.decode())


sqlite3.register_adapter(datetime, _adapt_datetime)
sqlite3.register_converter("DATETIME", _convert_datetime_int)


class DAO:
  def __init__(self, config: Config):

    self.conn = sqlite3.connect(config.db.path, detect_types=sqlite3.PARSE_DECLTYPES)

    self.links = LinkDAO(self.conn)
    if config.db.path == ":memory:":
      self.init_tables()

  def init_tables(self):
    self.links.setup()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    if exc_type:
      self.conn.rollback()
    else:
      self.conn.commit()
    self.conn.close()
