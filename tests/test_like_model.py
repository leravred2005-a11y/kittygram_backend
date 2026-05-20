"""Таблица 11 — Автотесты: Модель Like (3 теста)."""
import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from cats.models import Cat, Like

User = get_user_model()


@pytest.mark.django_db
class TestLikeModel:

    def setup_method(self):
        self.user = User.objects.create_user(username='user1', password='pass')
        self.cat = Cat.objects.create(
            name='Барсик', color='#808080', birth_year=2020, owner=self.user
        )

    def test_like_creation(self):
        """Создание лайка сохраняет связь user–cat."""
        like = Like.objects.create(user=self.user, cat=self.cat)
        assert like.pk is not None
        assert like.user == self.user
        assert like.cat == self.cat
        assert like.created_at is not None

    def test_like_uniqueness(self):
        """Нельзя создать два лайка от одного пользователя на одного кота."""
        Like.objects.create(user=self.user, cat=self.cat)
        with pytest.raises(IntegrityError):
            Like.objects.create(user=self.user, cat=self.cat)

    def test_like_cascade_delete(self):
        """При удалении кота его лайки удаляются каскадно."""
        Like.objects.create(user=self.user, cat=self.cat)
        assert Like.objects.filter(cat=self.cat).count() == 1
        self.cat.delete()
        assert Like.objects.filter(user=self.user).count() == 0
