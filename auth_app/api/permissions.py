from django.db.models import Q
from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanban_app.models import Boards

# Helper Function
def is_board_member(user, board):
    """
    Check if the user is a member of the board or the board owner.
    """
    return user == board.owner or user in board.members.all()

# Board Permissions
class IsOwnerOrMemberBoard(BasePermission):
    """
    Permission for Board access:
    - List views: allow access only if the user owns or is a member of at least one board
    - POST / Create: any authenticated user can create a board
    - Detail views: user must be owner or member
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # POST → any authenticated user can create a board
        if request.method == "POST":
            return True

        # List views → check ownership or membership
        if isinstance(view, (view.__class__,)) or hasattr(view, "queryset"):
            # Use a broad filter to see if user owns/is member of at least one board
            return Boards.objects.filter(Q(owner=user) | Q(members=user)).exists()

        # Detail views → permission checked in has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        # User must be owner or member
        user = request.user
        return is_board_member(user, obj)


# Task Permissions

class IsBoardMemberForTask(BasePermission):
    """
    Permission for Tasks:
    - POST / Create → only members or owner of the board can create a task
    - GET / Retrieve → only board members or owner can read
    - PUT/PATCH → only task author can edit
    - DELETE → only task author or board owner can delete
    """

    message = "User must be a member of the board to perform this action."

    def has_permission(self, request, view):
        """
        General permission for creating tasks (POST)
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method == "POST":
            board_id = request.data.get("board")
            if not board_id:
                return False  # board must be specified
            try:
                board = Boards.objects.get(id=board_id)
            except Boards.DoesNotExist:
                return False

            # Only board members or owner can create a task
            return user == board.owner or user in board.members.all()

        # For GET/List → object-level permission will enforce access
        return True

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for retrieving/editing/deleting a task
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # User is considered member if part of the board or owner
        is_member = user == obj.board.owner or user in obj.board.members.all()

        if request.method in SAFE_METHODS:
            # Only board members or owner can read
            return is_member

        # PUT/PATCH → only board owner can edit
        elif request.method in ["PUT", "PATCH"]:
            return user == obj.board.owner

        # DELETE → only board owner can delete
        elif request.method == "DELETE":
            return user == obj.board.owner

        return False
    

class IsCommentAuthorOrBoardMember(BasePermission):
    """
    - GET → board members or owner
    - POST → board members or owner
    - PUT/PATCH, DELETE → only comment author
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        # Read → board members
        if request.method in SAFE_METHODS:
            return user == obj.board.owner or user in obj.task.board.members.all()

        # Edit/Delete → only comment author
        return user == obj.author