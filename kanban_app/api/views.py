from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

# from achievements_app.models import Achievement
# from .serializers import AchievementSerializer


class TestApiView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({'message': 'running...'}, status=status.HTTP_200_OK)

class AchievementViewSet(viewsets.ModelViewSet):
    pass
    # serializer_class = AchievementSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        pass
        # return Achievement.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
