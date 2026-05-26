from django.contrib import admin
from .models import Cat, Like, Favorite

@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'owner')
    list_filter = ('color', 'owner')
    search_fields = ('name',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cat', 'created_at')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cat', 'created_at')