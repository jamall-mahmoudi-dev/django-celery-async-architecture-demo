import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_register_creates_user_and_dispatches_task(api_client):
    response = api_client.post(
        "/api/register/",
        {"username": "carol", "email": "carol@example.com", "password": "supersecret123"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["user"]["username"] == "carol"
    assert "task_id" in response.data
    assert User.objects.filter(username="carol").exists()


@pytest.mark.django_db
def test_register_rejects_duplicate_username(api_client):
    User.objects.create_user(username="dave", email="dave@example.com", password="whatever123")

    response = api_client.post(
        "/api/register/",
        {"username": "dave", "email": "new-dave@example.com", "password": "supersecret123"},
        format="json",
    )

    assert response.status_code == 400
    assert "username" in response.data


@pytest.mark.django_db
def test_task_status_endpoint_reports_success_after_registration(api_client):
    register_response = api_client.post(
        "/api/register/",
        {"username": "erin", "email": "erin@example.com", "password": "supersecret123"},
        format="json",
    )
    task_id = register_response.data["task_id"]

    status_response = api_client.get(f"/api/tasks/{task_id}/")

    assert status_response.status_code == 200
    assert status_response.data["status"] == "SUCCESS"
    assert status_response.data["result"] == "welcome email sent to erin@example.com"


@pytest.mark.django_db
def test_task_status_endpoint_unknown_id_is_pending(api_client):
    response = api_client.get("/api/tasks/nonexistent-task-id/")

    assert response.status_code == 200
    assert response.data["status"] == "PENDING"
