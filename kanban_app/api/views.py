from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from kanban_app.models import Boards
from .serializer import BoardsSerializer, CheckMailSerializer

class UserEmailList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        email = request.query_params.get("email")
        users = User.objects.filter(email=email).first()
        serializer = CheckMailSerializer(users)
        return Response(serializer.data)

class BoardView(APIView):
    def get(self, request):
        boards = Boards.objects.all()
        serializer = BoardsSerializer(boards, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = BoardsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer