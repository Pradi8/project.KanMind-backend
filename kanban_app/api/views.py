from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status, generics, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, GenericAPIView
from kanban_app.models import Boards, Comment, DashboardTasks
from .serializer import BoardDetailSerializer, BoardsSerializer, CheckMailSerializer, TasksSerializer, CommentSerializer
from auth_app.api.permissions import IsOwnerOrAdmin, IsOwnerOrMember
class UserEmailList(APIView):
    """
    API endpoint to retrieve a user by email.
    - GET request with 'email' as query parameter
    - Returns first matching user using CheckMailSerializer
    """
    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"detail": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_email(email)
        except ValidationError:
                return Response(
                {"detail": "Invalid email format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        users = User.objects.filter(email=email).first()
        if not users:
            return Response(
                {"detail": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CheckMailSerializer(users)
        return Response(serializer.data)
    
class BoardView(APIView):
    """
    API endpoint to list all boards with annotated metrics or create a new board.
    GET:
    - Returns list of boards with member count, ticket count, tasks to do count, and high-priority tasks count
    """
    def get(self, request):
        boards = Boards.objects.all()
        serializer = BoardsSerializer(boards, many=True)
        return Response(serializer.data)
    """
    POST:
    - Creates a new board with provided data
    """
    def post(self, request):
        serializer = BoardsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BoardSingleView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for a single board.
    - Supports GET, PUT/PATCH, DELETE
    """
    permission_classes = [IsOwnerOrMember]
    queryset = Boards.objects.all()
    serializer_class = BoardDetailSerializer
    
class TaskView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView):
    """
    API endpoint to list all tasks or create a new task.
    GET: Returns all tasks
    POST: Creates a new task
    """
    queryset = DashboardTasks.objects.all()
    serializer_class = TasksSerializer
    
    """
    GET: Returns all tasks
    """    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    """
    POST: Creates a new task
    """
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class TasksSingleView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for a single task.
    - Supports GET, PUT/PATCH, DELETE
    """
    permission_classes = [IsOwnerOrMember]
    queryset = DashboardTasks.objects.all()
    serializer_class = TasksSerializer

class AssignedTaskView(APIView):
    """
    API endpoint to get all tasks assigned to the requesting user.
    - GET request
    """
    permission_classes = [IsOwnerOrAdmin]
    def get(self, request):
        tasks = DashboardTasks.objects.filter(assignee_id=request.user)
        serializer = TasksSerializer(tasks, many=True)
        return Response(serializer.data)
    
class ReviewerTaskView(APIView):
    """
    API endpoint to get all tasks where the requesting user is the reviewer.
    - GET request
    """
    permission_classes = [IsOwnerOrAdmin]
    def get(self, request):
        tasks = DashboardTasks.objects.filter(reviewer_id=request.user)
        serializer = TasksSerializer(tasks, many=True)
        return Response(serializer.data)

class TaskCommentsView(APIView):
    """
    API endpoint to list or create comments for a specific task.
    GET:
    - Returns all comments for the task
    """
    def get(self, request, task_pk):
        task = get_object_or_404(DashboardTasks, pk=task_pk)
        comments = task.comments.all() 
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    """
    POST:
    - Creates a new comment linked to the task and current user
        URL Parameters:
    - task_pk (int): The primary key of the task to which the comment will be linked.
    - Saves the comment linking it to:
        • task = the retrieved task
        • author = current user
    """
    def post(self, request, task_pk):
        task = get_object_or_404(DashboardTasks, pk=task_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentSingleView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for a single comment.
    - Only the author or a superuser can update/delete
    - GET request available for all
    """
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return Comment.objects.filter(
            task_id=self.kwargs['task_pk']
        )