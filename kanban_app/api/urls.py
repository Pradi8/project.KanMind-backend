from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from .views import  BoardView, UserEmailList

# router = DefaultRouter()
# router.register(r'achievements', AchievementViewSet, basename='achievement')

urlpatterns = [
    path('email-check/', UserEmailList.as_view(), name='email-check'),
    path('boards/', BoardView.as_view(), name='board'),
    # path('boards/<int:pk>/', SingleBoardView.as_view(), name='board-detail'),
]