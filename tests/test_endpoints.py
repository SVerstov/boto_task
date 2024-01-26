import pytest

from fastapi.testclient import TestClient
import httpx


def test_get_all(client: TestClient):
    response = client.get("/api/links/all")
    assert response.status_code == 200


@pytest.fixture
def google_link_id(client: TestClient) -> str:
    link_params = {"url": "http://google.com", "status_code": 301}
    response = client.post("/api/links/create", json=link_params)
    return response.json()['short_url'].split('/')[-1]


@pytest.mark.asyncio
async def test_create_new_link(client: TestClient):
    link_params = {"url": "http://google.com", "status_code": 301}
    response = client.post("/api/links/create", json=link_params)
    assert response.status_code == 201

    link_id = response.json()['short_url'].split('/')[-1]
    assert response.status_code == 201

    response = client.get(f"/l/{link_id}", allow_redirects=False)
    assert response.status_code == 301
    assert response.next_request.url == "http://google.com"

    response = client.get("/api/links/all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_update_link(client: TestClient, google_link_id: str):
    update_params = {"url": "http://ya.ru", "status_code": 302}
    response = client.patch(f"/l/{google_link_id}", json=update_params)
    assert response.status_code == 200

    response = client.get(f"/l/{google_link_id}", allow_redirects=False)
    assert response.status_code == 302
    assert response.next_request.url == "http://ya.ru"


@pytest.mark.asyncio
async def test_delete_link(client: TestClient, google_link_id: str):
    response = client.delete(f"/l/{google_link_id}")
    assert response.status_code == 204

    response = client.get(f"/l/{google_link_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_not_found(client: TestClient):
    response = client.get('/l/ABCD')
    assert response.status_code == 404