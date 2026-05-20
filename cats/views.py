from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Achievement, Cat, Favorite, Like
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AchievementSerializer,
    CatSerializer,
    FavoriteSerializer,
    LikeSerializer,
)


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'top'):
            return [AllowAny()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    # ── Лайки ──────────────────────────────────────────────
    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        cat = self.get_object()
        if request.method == 'POST':
            _, created = Like.objects.get_or_create(user=request.user, cat=cat)
            if not created:
                return Response(
                    {'detail': 'Вы уже лайкнули этого кота.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {'detail': 'Лайк добавлен.', 'likes_count': cat.likes.count()},
                status=status.HTTP_201_CREATED,
            )
        deleted, _ = Like.objects.filter(user=request.user, cat=cat).delete()
        if not deleted:
            return Response(
                {'detail': 'Лайк не найден.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'detail': 'Лайк удалён.', 'likes_count': cat.likes.count()},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=['get'], url_path='liked',
            permission_classes=[IsAuthenticated])
    def liked(self, request):
        """Котики, которым пользователь поставил лайк."""
        cats = Cat.objects.filter(likes__user=request.user)
        page = self.paginate_queryset(cats)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(cats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='top',
            permission_classes=[AllowAny])
    def top(self, request):
        """Топ-10 котиков по количеству лайков."""
        cats = Cat.objects.annotate(
            total_likes=Count('likes')
        ).order_by('-total_likes')[:10]
        serializer = self.get_serializer(cats, many=True)
        return Response(serializer.data)

    # ── Избранное ───────────────────────────────────────────
    @action(detail=True, methods=['post', 'delete'],
            url_path='favorite', permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавить / убрать кота из избранного."""
        cat = self.get_object()
        if request.method == 'POST':
            fav, created = Favorite.objects.get_or_create(
                user=request.user, cat=cat
            )
            if not created:
                return Response(
                    {'detail': 'Кот уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = FavoriteSerializer(fav)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = Favorite.objects.filter(
            user=request.user, cat=cat
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Кот не был в избранном.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='favorites',
            permission_classes=[IsAuthenticated])
    def favorites(self, request):
        """Список котиков в избранном текущего пользователя."""
        favorites = Favorite.objects.filter(
            user=request.user
        ).select_related('cat')
        page = self.paginate_queryset(favorites)
        if page is not None:
            serializer = FavoriteSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    pagination_class = None
