import abc
from abc import ABC
from sqlite3 import Connection


class BaseDAO(ABC):
  _conn: Connection = None
  table_name: str = None

  @staticmethod
  def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
    return d

  @property
  def conn(self):
    return self._conn

  @conn.setter
  def conn(self, value):
    self._conn = value
    self._conn.row_factory = self._dict_factory

  @abc.abstractmethod
  def setup(self):
    pass

  def create(self, **kwargs):
    keys = kwargs.keys()
    values = tuple(kwargs.values())

    columns = ', '.join(keys)
    placeholders = ', '.join('?' * len(kwargs))

    query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
    self.conn.execute(query, values)

  def get_many(self, whereclauses: dict = None):
    query = f"SELECT * FROM {self.table_name}"
    where_values = []
    if whereclauses:
      set_where, where_values = self._split_dict_for_sql(whereclauses)
      query += f" WHERE {set_where}"
    cursor = self.conn.execute(query, where_values)
    return cursor.fetchall()

  def get_one(self, whereclauses: dict = None):
    query = f"SELECT * FROM {self.table_name}"
    where_values = []
    if whereclauses:
      set_where, where_values = self._split_dict_for_sql(whereclauses)
      query += f" WHERE {set_where}"
    query += " LIMIT 1"
    cursor = self.conn.execute(query, where_values)
    return cursor.fetchone()

  def update(self, whereclauses: dict, **updates):
    # todo I think that the function came out protected from sql injections,
    #  but I need to check
    if not whereclauses:
      raise ValueError("whereclause must be provided for update operation")

    set_upd, upd_values = self._split_dict_for_sql(updates)
    set_where, where_values = self._split_dict_for_sql(whereclauses)
    all_values = *upd_values, *where_values

    query = f"UPDATE {self.table_name} SET {set_upd} WHERE {set_where}"
    self.conn.execute(query, all_values)

  def delete(self, whereclauses: dict):
    set_where, where_values = self._split_dict_for_sql(whereclauses)
    query = f"DELETE FROM {self.table_name} WHERE {set_where}"
    cursor = self.conn.execute(query, where_values)
    return cursor.rowcount

  @staticmethod
  def _split_dict_for_sql(data: dict) -> tuple[str, tuple]:
    """
    split dict and prepare keys and values for sql query
    """
    set_values = ', '.join(f"{key} ?" for key in data.keys())
    return set_values, tuple(data.values())

  def count(self, whereclause: str = None, *args):
    query = f"SELECT COUNT(*) FROM {self.table_name}"
    if whereclause:
      query += f" WHERE {whereclause}"
    cursor = self.conn.execute(query, args)
    return cursor.fetchone()[0]
