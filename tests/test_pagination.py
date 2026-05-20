"""Таблица 11 — Автотесты: Пагинация (2 теста)."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from cats.models import Cat, Like

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def many_likes(db):
    user = User.objects.create_user(username='pag_user', password='pass')
    owner = User.objects.create_user(username='pag_owner', password='pass')
    cats = [
        Cat.objects.create(
            name=f'Cat{i}', color='#808080', birth_year=2020, owner=owner
        )
        for i in range(12)
    ]
    for cat in cats:
        Like.objects.create(user=user, cat=cat)
    return user, cats


@pytest.mark.django_db
class TestPagination:

    def test_page_size_limit(self, api_client, many_likes):
        """GET /api/likes/ — на первой странице не более PAGE_SIZE=10 объектов."""
        response = api_client.get('/api/likes/')
        assert response.status_code == 200
        assert len(response.data['results']) <= 10

    def test_next_previous_links(self, api_client, many_likes):
        """При наличии >10 лайков в ответе есть ссылка next."""
        response = api_client.get('/api/likes/')
        assert response.status_code == 200
        assert response.data['count'] > 10
        assert response.data['next'] is not None
