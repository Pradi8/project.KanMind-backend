from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AchievementViewSet, TestApiView

router = DefaultRouter()
router.register(r'achievements', AchievementViewSet, basename='achievement')

urlpatterns = [
    path('', include(router.urls)),
    path('test/', TestApiView.as_view(), name='api-test'),
]