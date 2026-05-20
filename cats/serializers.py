import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
import webcolors


import datetime as dt

from .models import Achievement, AchievementCat, Cat, Favorite, Like


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value
    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(required=False, many=True)
    color = Hex2NameColor()
    age = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()

    class Meta:
        model = Cat
        fields = (
            'id', 'name', 'color', 'birth_year', 'achievements', 'owner', 'age',
            'image', 'likes_count', 'is_liked', 'is_favorited', 'favorites_count'
        )
        read_only_fields = ('owner',)

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

    def get_favorites_count(self, obj):
        return obj.favorited_by.count()

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year
    
    def create(self, validated_data):
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat
        else:
            achievements = validated_data.pop('achievements')
            cat = Cat.objects.create(**validated_data)
            for achievement in achievements:
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement
                    )
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=cat
                    )
            return cat
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.color = validated_data.get('color', instance.color)
        instance.birth_year = validated_data.get(
            'birth_year', instance.birth_year
            )
        instance.image = validated_data.get('image', instance.image)
        if 'achievements' in validated_data:
            achievements_data = validated_data.pop('achievements')
            lst = []
            for achievement in achievements_data:
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement
                    )
                lst.append(current_achievement)
            instance.achievements.set(lst)

        instance.save()
        return instance

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'cat', 'user')
        read_only_fields = ('user',)


class FavoriteSerializer(serializers.ModelSerializer):
    cat_name = serializers.CharField(source='cat.name', read_only=True)
    cat_color = serializers.CharField(source='cat.color', read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'cat', 'cat_name', 'cat_color', 'created_at')
        read_only_fields = ('user', 'created_at')
