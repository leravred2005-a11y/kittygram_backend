"""Таблица 11 — Автотесты: Представления CatLikeView (5 тестов)."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from cats.models import Cat, Like

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(username='clv_user', password='pass')
    token, _ = Token.objects.get_or_create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client, user


@pytest.fixture
def cat(auth_client):
    _, user = auth_client
    return Cat.objects.create(
        name='Рыжик', color='#FF8C00', birth_year=2021, owner=user
    )


@pytest.mark.django_db
class TestCatLikeView:

    def test_post_like_success(self, auth_client, cat):
        """POST /api/cats/{id}/like/ — лайк добавляется, статус 201."""
        client, _ = auth_client
        response = client.post(f'/api/cats/{cat.pk}/like/')
        assert response.status_code == 201
        assert Like.objects.filter(cat=cat).count() == 1

    def test_post_like_duplicate(self, auth_client, cat):
        """POST /api/cats/{id}/like/ повторно — статус 400."""
        client, user = auth_client
        Like.objects.create(user=user, cat=cat)
        response = client.post(f'/api/cats/{cat.pk}/like/')
        assert response.status_code == 400
        assert 'detail' in response.data

    def test_get_like_check_authenticated(self, auth_client, cat):
        """GET /api/cats/{id}/like/ авторизованным — возвращает is_liked и likes_count."""
        client, user = auth_client
        Like.objects.create(user=user, cat=cat)
        response = client.get(f'/api/cats/{cat.pk}/like/')
        assert response.status_code == 200
        assert response.data['is_liked'] is True
        assert response.data['likes_count'] == 1

    def test_delete_like_success(self, auth_client, cat):
        """DELETE /api/cats/{id}/like/ — лайк удаляется, статус 204."""
        client, user = auth_client
        Like.objects.create(user=user, cat=cat)
        response = client.delete(f'/api/cats/{cat.pk}/like/')
        assert response.status_code == 204
        assert Like.objects.filter(cat=cat, user=user).count() == 0

    def test_delete_like_unauthenticated(self, api_client, cat):
        """DELETE /api/cats/{id}/like/ без авторизации — ошибка 401/403."""
        response = api_client.delete(f'/api/cats/{cat.pk}/like/')
        assert response.status_code in (401, 403)
