"""Таблица 11 — Автотесты: Представления LikeViewSet (4 теста)."""
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
def user_with_token(db):
    user = User.objects.create_user(username='like_vs_user', password='pass')
    token, _ = Token.objects.get_or_create(user=user)
    return user, token.key


@pytest.fixture
def cat_and_like(user_with_token):
    user, _ = user_with_token
    cat = Cat.objects.create(
        name='Снежок', color='#FFFFFF', birth_year=2022, owner=user
    )
    like = Like.objects.create(user=user, cat=cat)
    return cat, like


@pytest.mark.django_db
class TestLikeViewSet:

    def test_get_like_list(self, api_client, cat_and_like):
        """GET /api/likes/ — возвращает список лайков со статусом 200."""
        response = api_client.get('/api/likes/')
        assert response.status_code == 200
        assert 'results' in response.data
        assert response.data['count'] >= 1

    def test_get_like_retrieve(self, api_client, cat_and_like):
        """GET /api/likes/{id}/ — возвращает конкретный лайк со статусом 200."""
        _, like = cat_and_like
        response = api_client.get(f'/api/likes/{like.pk}/')
        assert response.status_code == 200
        assert response.data['id'] == like.pk

    def test_delete_like_by_owner(self, api_client, user_with_token, cat_and_like):
        """DELETE /api/likes/{id}/ владельцем — удаляет лайк (204)."""
        user, token = user_with_token
        _, like = cat_and_like
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = api_client.delete(f'/api/likes/{like.pk}/')
        assert response.status_code == 204
        assert not Like.objects.filter(pk=like.pk).exists()

    def test_delete_like_unauthenticated(self, api_client, cat_and_like):
        """DELETE /api/likes/{id}/ без авторизации — ошибка 401/403."""
        _, like = cat_and_like
        response = api_client.delete(f'/api/likes/{like.pk}/')
        assert response.status_code in (401, 403)
