import pytest

from src import dao
from src.config import Config


@pytest.fixture
def create_3_links(config: Config):
  with dao.get_conn(config.db_name) as conn:
    for i in range(1, 4):
      dao.create(
        conn=conn,
        link_id=f"test{i}",
        url="http://example.com",
        status_code=301
      )


def test_create_and_get(config: Config):
  with dao.get_conn(config.db_name) as conn:
    link_id = dao.create_link(
      conn=conn,
      link_id_len=config.id_len,
      url="http://example.com",
      status_code=301
    )

    new_link = dao.get_by_link_id(conn, link_id)
    assert new_link['link_id'] == link_id


@pytest.mark.usefixtures("create_3_links")
def test_get_all(config):
  with dao.get_conn(config.db_name) as conn:
    res = dao.get_all(conn)
    assert len(res) == 3


@pytest.mark.usefixtures("create_3_links")
def test_increase_counter(config: Config):
  with dao.get_conn(config.db_name) as conn:
    dao.increase_counter(conn, "test1")
    dao.increase_counter(conn, "test1")
    res = dao.get_by_link_id(conn, "test1")
    assert res["counter"] == 2


@pytest.mark.usefixtures("create_3_links")
def test_delete(config: Config):
  with dao.get_conn(config.db_name) as conn:
    count = dao.delete_link(conn, "test2")
    assert count == 1
    count = dao.delete_link(conn, "test2")
    assert count == 0

  with dao.get_conn(config.db_name) as conn:
    res = dao.get_all(conn)
    assert len(res) == 2


@pytest.mark.usefixtures("create_3_links")
def test_update(config: Config):
  with dao.get_conn(config.db_name) as conn:
    new_url = "http://new.url"
    dao.update_link(conn, link_id="test1", url="http://new.url", status_code=302)
  with dao.get_conn(config.db_name) as conn:
    res = dao.get_by_link_id(conn, "test1")
    assert res['url'] == new_url
    assert res['status_code'] == 302
    pass
