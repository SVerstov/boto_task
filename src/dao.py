import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from sqlite3 import Connection


def _adapt_datetime(dt: datetime):
  return dt.isoformat()


def _convert_datetime_int(dt_bytes: bytes):
  return datetime.fromisoformat(dt_bytes.decode())


sqlite3.register_adapter(datetime, _adapt_datetime)
sqlite3.register_converter("DATETIME", _convert_datetime_int)


def setup_db(conn: Connection):
  conn.execute(
    """
      CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY,
        link_id TEXT UNIQUE,
        url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        counter INTEGER DEFAULT 0,
        status_code INTEGER DEFAULT 301
        );
      """
  )
  conn.commit()


def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d


def create(conn: Connection, link_id: str, url: str, status_code: int):
  query = "INSERT INTO links (link_id, url, status_code) VALUES (?, ?, ?)"
  conn.execute(query, (link_id, url, status_code))
  return link_id


def create_link(conn: Connection, link_id_len: int, url: str, status_code: int) -> str:
  while True:
    try:
      link_id = str(uuid.uuid4())[:link_id_len]
      query = "INSERT INTO links (link_id, url, status_code) VALUES (?, ?, ?)"
      conn.execute(query, (link_id, url, status_code))
      return link_id
    except sqlite3.IntegrityError:
      # regenerate if collision occur
      continue


def get_by_link_id(conn: Connection, link_id: str) -> dict:
  query = """
  SELECT * FROM links
  WHERE link_id = ?
  """
  cur = conn.execute(query, (link_id,))
  return cur.fetchone()


def increase_counter(conn: Connection, link_id: str):
  query = """
  UPDATE links
  SET counter = counter + 1
  WHERE link_id = ?
  """
  cur = conn.execute(query, (link_id,))
  return cur.fetchone()


def get_all(conn: Connection):
  cur = conn.execute("SELECT * FROM links")
  return cur.fetchall()


def delete_link(conn: Connection, link_id: str):
  query = """
  DELETE FROM links
  WHERE link_id = ?
  """
  cur = conn.execute(query, (link_id,))
  return cur.rowcount


def update_link(conn: Connection, link_id: str, url: str, status_code: int):
  query = """
  UPDATE links
  SET url = ?, status_code = ?
  WHERE link_id = ?
  """
  cur = conn.execute(query, (url, status_code, link_id))
  return cur.rowcount


@contextmanager
def get_conn(db_filename: Path | str):
  conn = sqlite3.connect(db_filename, detect_types=sqlite3.PARSE_DECLTYPES)
  conn.row_factory = dict_factory
  try:
    yield conn
    conn.commit()
  except Exception:
    # todo what we should catch here?
    conn.rollback()
    raise
  finally:

    conn.close()
