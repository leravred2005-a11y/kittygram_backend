from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Achievement(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Cat(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16)
    birth_year = models.IntegerField()
    owner = models.ForeignKey(
        User, related_name='cats', 
        on_delete=models.CASCADE
        )
    achievements = models.ManyToManyField(Achievement, through='AchievementCat')
    image = models.ImageField(
        upload_to='cats/images/', 
        null=True,  
        default=None
        )

    def __str__(self):
        return self.name


class AchievementCat(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.achievement} {self.cat}'


class Like(models.Model):
    user = models.ForeignKey(
        User, related_name='likes',
        on_delete=models.CASCADE
    )
    cat = models.ForeignKey(
        Cat, related_name='likes',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'cat')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} likes {self.cat}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, related_name='favorites',
        on_delete=models.CASCADE
    )
    cat = models.ForeignKey(
        Cat, related_name='favorited_by',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'cat')

    def __str__(self):
        return f'{self.user} → {self.cat}'