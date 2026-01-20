from django.db.models import Q
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import generics
from kanban_app.models import Boards

class IsOwnerOrMemberList(BasePermission):
    """
    Custom Permission:
    - List views: allow access only if the user owns or is a member of at least one board
    - POST / Create: any authenticated user can create a board
    - Detail views: access is checked in has_object_permission
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # POST / Create → any authenticated user can create a board
        if request.method == "POST":
            return True

        # List views → check ownership or membership
        if isinstance(view, (generics.ListAPIView, generics.ListCreateAPIView)):
            return Boards.objects.filter(Q(owner=user) | Q(members=user)).exists()

        # Detail views → will be checked in has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        # Detail view permission: user must be owner or member
        return obj.owner == request.user or request.user in obj.members.all()
    
class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to allow:
    - Safe methods (GET, HEAD, OPTIONS) for everyone
    - DELETE only for superusers or the object's author
    - Other methods (PUT, PATCH) only for the object's author
    """
    def has_object_permission(self, request, view, obj):
        # Allow read-only requests for any authenticated user
        if request.method in SAFE_METHODS:
            return True
        # Allow DELETE requests if the user is a superuser or the author of the object
        elif request.method == "DELETE":
             return bool(
                request.user and (
                    request.user.is_superuser or
                    request.user == obj.author
                )
            )
        # For other unsafe methods (PUT, PATCH), only allow if the user is the author
        else:
            return bool(request.user and request.user == obj.author)
        
class IsOwnerOrMember(BasePermission):
    """
    Custom permission to allow:
    - GET: nur Owner oder Members
    - PUT, PATCH only for superusers, members or the object's owner
    - DELETE only for superusers or the object's owner
    """
    def has_object_permission(self, request, view, obj,):
        # Get the current user
        user = request.user
        # Block access if the user is not authenticated
        if not user or not user.is_authenticated:
            return False
        # Try to get the owner directly from the object (e.g. Board)
        owner = getattr(obj, "owner", None)
        # Try to get members directly from the object if available
        members = obj.members.all() if hasattr(obj, "members") else []
        # If the object has no direct owner (e.g. Task),
        # use the related board's owner and members
        if owner is None and hasattr(obj, "board") and obj.board:
            owner = obj.board.owner
            members = obj.board.members.all()
                # GET nur Owner oder Members
        if request.method == "GET":
            return user == owner or user in members
         # Allow PUT and PATCH requests for superusers, owners, or members
        if request.method in ["PUT", "PATCH"]:
            return user.is_superuser or user == owner or user in members
        # Allow DELETE requests only for superusers or the owner
        if request.method == "DELETE":
            return user.is_superuser or user == owner

        return False
    
class IsBoardMemberForTask(BasePermission):
    """
    Allows only members or the owner of a board 
    to create tasks for that board.
    """
    message = "Der Benutzer muss Mitglied des Boards sein, um eine Task zu erstellen."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False  

        # POST → the board must exist and the user must be a member
        if request.method == "POST":
            board_id = request.data.get("board")
            if not board_id:
                return False  
            try:
                board = Boards.objects.get(id=board_id)
            except Boards.DoesNotExist:
                # Existence check → 404 handled in the view
                return True

            # Return False (403) if the user is not a member or the owner
            return user in board.members.all() or board.owner == user

        # GET / List → only login is required
        return True
    
    
        
class IsBoardMemberForSingleTask(BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Prüfen, ob der Benutzer Mitglied des Boards ist
        is_board_member = user in obj.board.members.all() or obj.board.owner == user

        # SAFE_METHODS → nur Board-Mitglieder dürfen lesen
        if request.method in SAFE_METHODS:
            return is_board_member

        # DELETE → nur Autor oder Superuser
        elif request.method == "DELETE":
            return bool(user and (user.is_superuser or user == obj.author))

        # PUT/PATCH → nur der Autor darf bearbeiten
        else:
            return bool(user and user == obj.author)