"""Таблица 11 — Автотесты: Сериализаторы (1 тест)."""
import pytest
from django.contrib.auth import get_user_model

from cats.models import Cat, Like
from cats.serializers import LikeSerializer

User = get_user_model()


@pytest.mark.django_db
class TestLikeSerializer:

    def test_like_serializer_fields(self):
        """Сериализатор выводит поля id, user, cat_name, created_at."""
        user = User.objects.create_user(username='ser_user', password='pass')
        cat = Cat.objects.create(
            name='Мурзик', color='#FFA500', birth_year=2021, owner=user
        )
        like = Like.objects.create(user=user, cat=cat)

        data = LikeSerializer(like).data

        assert 'id' in data
        assert 'user' in data
        assert 'cat_name' in data
        assert 'created_at' in data
        assert data['cat_name'] == 'Мурзик'
        assert data['user'] == 'ser_user'
