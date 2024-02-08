import sqlite3
import uuid
from sqlite3 import Connection

from dao import BaseDAO


class LinkDAO(BaseDAO):
  def __init__(self, conn: Connection):
    self.conn = conn
    self.table_name = "short_links"

  def setup(self):
    self.conn.execute(
      f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
          id INTEGER PRIMARY KEY,
          link_id TEXT UNIQUE,
          url TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          counter INTEGER DEFAULT 0,
          status_code INTEGER DEFAULT 301
          );
        """
    )
    self.conn.commit()

  def create_short_link(self, link_len: int, **kwargs) -> str:
    while True:
      try:
        link_id = str(uuid.uuid4())[:link_len]
        self.create(link_id=link_id, **kwargs)
        return link_id
      except sqlite3.IntegrityError:
        # regenerate if collision occur
        continue

  def get_by_link_id(self, link_id: str) -> dict:
    return self.get_one({"link_id =": link_id})

  def increase_counter(self, link_id: str):
    query = f"""
    UPDATE {self.table_name}
    SET counter = counter + 1
    WHERE link_id = ?
    """
    self.conn.execute(query, (link_id,))
