"""Таблица 11 — Автотесты: Права доступа (2 теста)."""
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
def two_users(db):
    owner = User.objects.create_user(username='perm_owner', password='pass')
    other = User.objects.create_user(username='perm_other', password='pass')
    owner_token, _ = Token.objects.get_or_create(user=owner)
    other_token, _ = Token.objects.get_or_create(user=other)
    return owner, owner_token.key, other, other_token.key


@pytest.mark.django_db
class TestPermissions:

    def test_other_user_cannot_delete_like(self, api_client, two_users):
        """Авторизованный пользователь не может удалить чужой лайк (403)."""
        owner, owner_token, other, other_token = two_users
        cat = Cat.objects.create(
            name='Персик', color='#FFA500', birth_year=2020, owner=owner
        )
        like = Like.objects.create(user=owner, cat=cat)

        api_client.credentials(HTTP_AUTHORIZATION=f'Token {other_token}')
        response = api_client.delete(f'/api/likes/{like.pk}/')
        assert response.status_code == 403
        assert Like.objects.filter(pk=like.pk).exists()

    def test_other_user_cannot_delete_cat(self, api_client, two_users):
        """Авторизованный пользователь не может удалить чужого кота (403)."""
        owner, owner_token, other, other_token = two_users
        cat = Cat.objects.create(
            name='Пушок', color='#FFFFFF', birth_year=2021, owner=owner
        )

        api_client.credentials(HTTP_AUTHORIZATION=f'Token {other_token}')
        response = api_client.delete(f'/api/cats/{cat.pk}/')
        assert response.status_code == 403
        assert Cat.objects.filter(pk=cat.pk).exists()
