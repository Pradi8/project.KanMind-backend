from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from rest_framework import status, generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, GenericAPIView, ListCreateAPIView
from rest_framework.exceptions import NotFound
from kanban_app.models import Boards, Comment, DashboardTasks
from .serializer import BoardDetailSerializer, BoardsSerializer, CheckMailSerializer, TaskDetailSerializer, TasksSerializer, CommentSerializer
from auth_app.api.permissions import IsBoardMemberForTask, IsOwnerOrMemberBoard, IsCommentAuthorOrBoardMember

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
    permission_classes = [IsAuthenticated]
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
    queryset = Boards.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMemberBoard]

    def get_object(self):
        """
        First, check if the board exists → 404
        Then DRF automatically handles the permissions
        """
        obj = super().get_object()
        return obj
    
class TaskView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView):
    """
    API endpoint to list all tasks or create a new task.
    GET: Returns all tasks
    POST: Creates a new task
    """
    queryset = DashboardTasks.objects.all()
    serializer_class = TasksSerializer
    permission_classes = [IsBoardMemberForTask]

    def post(self, request, *args, **kwargs):
        board_id = request.data.get("board")

        # Check if the board exists → return 404 if not found
        try:
            board = Boards.objects.get(pk=board_id)
        except Boards.DoesNotExist:
            raise NotFound("Board does not exist.")
        user = request.user
        if board.owner != user and user not in board.members.all():
            raise PermissionDenied("User must be a member of the board to perform this action.")

        # Serialize the data and save the new task
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(board=board)  
        return Response(serializer.data, status=201)


class TasksSingleView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for a single task.
    - Supports GET, PUT/PATCH, DELETE
    """
    queryset = DashboardTasks.objects.all()
    permission_classes = [IsBoardMemberForTask]
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
    permission_classes = [IsBoardMemberForTask]
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
    permission_classes = [IsAuthenticated, IsCommentAuthorOrBoardMember]
    def get(self, request, task_pk):
        task = get_object_or_404(DashboardTasks, pk=task_pk)
        if not task.board:
            raise PermissionDenied("Task is not assigned to a board.")

        user = request.user
        board = task.board
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("User must be a member of the board to view comments.")

        comments = Comment.objects.filter(task=task)
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

        # Check if task has a board
        if not task.board:
            raise PermissionDenied("Task is not assigned to a board.")

        board = task.board
        user = request.user

        # Only Board owner or member can post
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("User must be a member of the board to comment.")

        # Create the comment
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class CommentSingleView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for a single comment.
    - Only the author or a superuser can update/delete
    - GET request available for all
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthorOrBoardMember]

    def get_queryset(self):
        # Filter comments for the specific task and the individual comment
        task_pk = self.kwargs['task_pk']
        return Comment.objects.filter(task_id=task_pk)