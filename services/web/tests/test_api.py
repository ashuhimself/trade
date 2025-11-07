import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAPI:
    def test_health_check(self):
        client = APIClient()
        response = client.get("/health/")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_exchanges_list(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/exchanges/")

        assert response.status_code == 200
