from random import randint

import pytest

from fastapi.testclient import TestClient

from db import DAO, ShortLink


@pytest.fixture
def google_link_id(client: TestClient) -> str:
    link_params = {"url": "http://google.com", "status_code": 301}
    response = client.post("/api/links/create", json=link_params)
    return response.json()['short_url'].split('/')[-1]


@pytest.fixture
def create_10_links(client: TestClient):
    for i in range(10):
        link_params = {"url": "http://google.com", "status_code": 301}
        response = client.post("/api/links/create", json=link_params)
        assert response.status_code == 201


def test_create_new_link(client: TestClient):
    link_params = {"url": "http://google.com", "status_code": 301}
    response = client.post("/api/links/create", json=link_params)
    assert response.status_code == 201

    link_id = response.json()['short_url'].split('/')[-1]
    assert response.status_code == 201

    response = client.get(f"/{link_id}", allow_redirects=False)
    assert response.status_code == 301
    assert str(response.next_request.url).rstrip('/') == "http://google.com"

    response = client.get("/api/links/all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_update_link(client: TestClient, google_link_id: str):
    update_params = {"url": "http://ya.ru", "status_code": 302}
    response = client.patch(f"/api/links/{google_link_id}", json=update_params)
    assert response.status_code == 200

    response = client.get(f"/{google_link_id}", allow_redirects=False)
    assert response.status_code == 302
    assert str(response.next_request.url).rstrip('/') == "http://ya.ru"

    update_params = {"status_code": 301}
    response = client.patch(f"/api/links/{google_link_id}", json=update_params)
    assert response.status_code == 200

    response = client.get(f"/{google_link_id}", allow_redirects=False)
    assert response.status_code == 301


def test_delete_link(client: TestClient, google_link_id: str):
    response = client.delete(f"/api/links/{google_link_id}")
    assert response.status_code == 204

    response = client.get(f"/{google_link_id}")
    assert response.status_code == 404


def test_not_found(client: TestClient):
    response = client.get('/ABCD')
    assert response.status_code == 404


def test_counter(client: TestClient, google_link_id):
    for _ in range(3):
        response = client.get(f"/{google_link_id}", allow_redirects=False)
        assert response.status_code == 301

    response = client.get(f"/api/links/{google_link_id}")
    assert response.status_code == 200
    data = response.json()
    assert data.get('counter') == 3


@pytest.mark.usefixtures("create_10_links")
def test_get_all(client: TestClient):
    response = client.get("/api/links/all")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10


def test_create_bad_url(client: TestClient):
    link_params = {"url": "google.com", "status_code": 301}
    response = client.post("/api/links/create", json=link_params)
    assert response.status_code == 422
