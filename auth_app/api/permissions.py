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