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


@pytest.mark.django_db
def test_post_profile_already_exist(
    create_profile,
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
    assert response.status_code == 400


@pytest.mark.django_db
def test_post_profile_invalid_age(
    authenticated_client,
    job,
    sleep_time,
    delay_reason,
    username,
):
    url = reverse("profile")
    data = {
        "username": username,
        "age": "33",
        "job": job,
        "sleep_time": sleep_time,
        "delay_reason": delay_reason,
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_get_profile_success(
    create_profile,
    authenticated_client,
):
    url = reverse("profile")
    response = authenticated_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_profile_not_exist(
    authenticated_client,
):
    url = reverse("profile")
    response = authenticated_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_patch_profile_success(
    create_profile,
    authenticated_client,
    username,
):
    url = reverse("profile")
    data = {
        "username": username + "updated",
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["username"] == username + "updated"


@pytest.mark.django_db
def test_patch_profile_not_found(
    authenticated_client,
    username,
):
    url = reverse("profile")
    data = {
        "username": username + "updated",
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 404


@pytest.mark.django_db
def test_patch_profile_user_id_update(
    authenticated_client,
    username,
):
    url = reverse("profile")
    data = {
        "user_id": "99",
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_patch_profile_invalid_data(
    create_profile,
    authenticated_client,
    username,
):
    url = reverse("profile")
    data = {
        "age": "33",
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400
