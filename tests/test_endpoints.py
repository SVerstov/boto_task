import pytest
import pytest_asyncio

from fastapi.testclient import TestClient
import httpx

from db import DAO, ShortLink


@pytest.fixture
def google_link_id(client: TestClient) -> str:
    link_params = {"url": "http://google.com", "status_code": 301}
    response = client.post("/api/links/create", json=link_params)
    return response.json()['short_url'].split('/')[-1]


@pytest_asyncio.fixture
async def create_10_links(dao: DAO):
    for i in range(10):
        dao.session.add(ShortLink(
            link_id=f'abc{i}',
            url="http://google.com",
        ))
    await dao.session.commit()


@pytest.mark.asyncio
async def test_create_new_link(client: TestClient):
    link_params = {"url": "http://google.com", "status_code": 301}
    response = client.post("/api/links/create", json=link_params)
    assert response.status_code == 201

    link_id = response.json()['short_url'].split('/')[-1]
    assert response.status_code == 201

    response = client.get(f"/l/{link_id}", allow_redirects=False)
    assert response.status_code == 301
    assert str(response.next_request.url).rstrip('/') == "http://google.com"

    response = client.get("/api/links/all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_update_link(client: TestClient, google_link_id: str):
    update_params = {"url": "http://ya.ru", "status_code": 302}
    response = client.patch(f"/api/links/{google_link_id}", json=update_params)
    assert response.status_code == 200

    response = client.get(f"/l/{google_link_id}", allow_redirects=False)
    assert response.status_code == 302
    assert str(response.next_request.url).rstrip('/') == "http://ya.ru"


@pytest.mark.asyncio
async def test_delete_link(client: TestClient, google_link_id: str):
    response = client.delete(f"/api/links/{google_link_id}")
    assert response.status_code == 204

    response = client.get(f"/l/{google_link_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_not_found(client: TestClient):
    response = client.get('/l/ABCD')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_counter(client: TestClient, dao: DAO, google_link_id):
    response = client.get(f"/l/{google_link_id}")
    response = client.get(f"/l/{google_link_id}")
    obj = await dao.short_link.get_by_link_id(google_link_id)
    assert obj.counter == 2


@pytest.mark.asyncio
async def test_get_all(client: TestClient, create_10_links):
    response = client.get("/api/links/all")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
