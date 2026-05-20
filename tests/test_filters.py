"""Таблица 11 — Автотесты: Фильтрация и поиск (2 теста)."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from cats.models import Cat, Like

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def likes_dataset(db):
    user = User.objects.create_user(username='filter_user', password='pass')
    cat1 = Cat.objects.create(name='Мурзик', color='#808080', birth_year=2020, owner=user)
    cat2 = Cat.objects.create(name='Барсик', color='#000000', birth_year=2021, owner=user)
    like1 = Like.objects.create(user=user, cat=cat1)
    like2 = Like.objects.create(user=user, cat=cat2)
    return user, cat1, cat2, like1, like2


@pytest.mark.django_db
class TestFilters:

    def test_filter_by_cat(self, api_client, likes_dataset):
        """GET /api/likes/?cat={id} — возвращает только лайки указанного кота."""
        _, cat1, cat2, like1, like2 = likes_dataset
        response = api_client.get(f'/api/likes/?cat={cat1.pk}')
        assert response.status_code == 200
        ids = [item['id'] for item in response.data['results']]
        assert like1.pk in ids
        assert like2.pk not in ids

    def test_search_by_cat_name(self, api_client, likes_dataset):
        """GET /api/likes/?cat_name=Мурз — возвращает лайки с подходящим именем кота."""
        _, cat1, cat2, like1, like2 = likes_dataset
        response = api_client.get('/api/likes/?cat_name=Мурз')
        assert response.status_code == 200
        ids = [item['id'] for item in response.data['results']]
        assert like1.pk in ids
        assert like2.pk not in ids
