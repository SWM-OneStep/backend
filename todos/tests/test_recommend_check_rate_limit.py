# import asyncio
import time
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken


@pytest.mark.django_db
@pytest.mark.asyncio
@patch("todos.views.openai_client.chat.completions.create")
async def test_rate_limit_exceeded(
    mock_llm, create_user, create_todo, recommend_result
):
    mock_llm.return_value = recommend_result
    url = "https://dev.stepby.one/todos/recommend/"
    access_token = str(AccessToken.for_user(create_user))

    async with httpx.AsyncClient() as client:
        # Attach the Authorization header with the Bearer token
        client.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
        )
        response = await client.get(url, params={"todo_id": create_todo.id})
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        print(response)
    assert response.status_code == status.HTTP_200_OK

    async with httpx.AsyncClient() as client:
        # Attach the Authorization header with the Bearer token
        client.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
        )
        response = await client.get(url, params={"todo_id": create_todo.id})
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.json()["error"] == "Rate limit exceeded"


@pytest.mark.django_db
@pytest.mark.asyncio
@patch(
    "todos.views.openai_client.chat.completions.create", new_callable=AsyncMock
)
def test_rate_limit_passed(
    mock_llm, authenticated_client, create_todo, recommend_result
):
    url = "https://dev.stepby.one/todos/recommend/"
    mock_llm.return_value = recommend_result

    response = authenticated_client.get(url, {"todo_id": create_todo.id})
    assert response.status_code == status.HTTP_200_OK

    time.sleep(10)  # Non-blocking sleep

    response = authenticated_client.get(url, {"todo_id": create_todo.id})
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.asyncio
@patch("todos.views.openai_client.chat.completions.create")
async def test_rate_limit_premium(
    mock_llm, authenticated_client, create_user, create_todo, recommend_result
):
    create_user.is_premium = True
    create_user.save()

    url = reverse("recommend")
    mock_llm.return_value = recommend_result

    response = authenticated_client.get(url, {"todo_id": create_todo.id})
    assert response.status_code == status.HTTP_200_OK

    response = authenticated_client.get(url, {"todo_id": create_todo.id})
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_recommend_benchmark(
    benchmark, authenticated_client, create_todo
):
    url = reverse("recommend")

    async def async_benchmark():
        response = await authenticated_client.get(
            url, {"todo_id": create_todo.id}
        )
        return response

    response = await benchmark(async_benchmark)
    assert response.status_code == status.HTTP_200_OK
