from rest_framework.permissions import BasePermission, SAFE_METHODS

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
    - Safe methods (GET, HEAD, OPTIONS) for everyone
    - PUT, PATCH only for superusers, members or the object's owner
    - DELETE only for superusers or the object's owner
    """
    def has_object_permission(self, request, view, obj,):
        # Allow read-only requests for any authenticated user
        if request.method in SAFE_METHODS:
            return True
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
         # Allow PUT and PATCH requests for superusers, owners, or members
        if request.method in ["PUT", "PATCH"]:
            return user.is_superuser or user == owner or user in members
        # Allow DELETE requests only for superusers or the owner
        if request.method == "DELETE":
            return user.is_superuser or user == owner

        return False