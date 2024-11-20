import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_post_profile_success(
    authenticated_client,
    job,
    sleep_time,
    age,
    delay_reason,
    username,
):
    url = reverse("profile")
    data = {
        "username": username,
        "age": age,
        "job": job,
        "sleep_time": sleep_time,
        "delay_reason": delay_reason,
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["username"] == username
