import pytest
from rest_framework.test import APIClient

HEALTH_URL = "/api/health/"


@pytest.fixture
def client():
    return APIClient()


def test_health_returns_ok_without_login(client):
    response = client.get(HEALTH_URL)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_rejects_post(client):
    response = client.post(HEALTH_URL)

    assert response.status_code == 405


def test_health_ignores_invalid_credentials(client):
    # A malformed Basic header makes DRF's default BasicAuthentication reject the
    # request (403) unless the view opts out of authentication entirely.
    response = client.get(HEALTH_URL, HTTP_AUTHORIZATION="Basic not-base64!")

    assert response.status_code == 200
