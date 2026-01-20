from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status, generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, GenericAPIView, ListCreateAPIView
from kanban_app.models import Boards, Comment, DashboardTasks
from .serializer import BoardDetailSerializer, BoardsSerializer, CheckMailSerializer, TaskDetailSerializer, TasksSerializer, CommentSerializer
from auth_app.api.permissions import IsBoardMemberForSingleTask, IsBoardMemberForTask, IsOwnerOrAdmin, IsOwnerOrMember, IsOwnerOrMemberList
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
    
class BoardView(ListCreateAPIView):
    """
    API endpoint to list all boards with annotated metrics or create a new board.
    GET:
    - Returns list of boards with member count, ticket count, tasks to do count, and high-priority tasks count
    """
    serializer_class = BoardsSerializer
    permission_classes = [IsOwnerOrMemberList]
    queryset = Boards.objects.all()
    def get_queryset(self):
        user = self.request.user
        return Boards.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
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
    permission_classes = [IsOwnerOrMemberList, IsBoardMemberForTask]
    
    """
    GET: Returns all tasks
    """    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    """
    POST: Creates a new task
    """
    def post(self, request, *args, **kwargs):
        board_id = request.data.get("board")
        try:
            board = Boards.objects.get(id=board_id)
        except Boards.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Board nicht gefunden. Die angegebene Board-ID existiert nicht.")
        return self.create(request, *args, **kwargs)

class TasksSingleView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for a single task.
    - Supports GET, PUT/PATCH, DELETE
    """
    permission_classes = [IsBoardMemberForSingleTask]
    queryset = DashboardTasks.objects.all()
    def get_queryset(self):
        return DashboardTasks.objects.filter(board__members=self.request.user)
    serializer_class = TaskDetailSerializer

class AssignedTaskView(APIView):
    """
    API endpoint to get all tasks assigned to the requesting user.
    - GET request
    """
    permission_classes = [IsAuthenticated]
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