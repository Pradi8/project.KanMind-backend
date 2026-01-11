from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method == "DELETE":
             return bool(
                request.user and (
                    request.user.is_superuser or
                    request.user == obj.author
                )
            )
        else:
            return bool(request.user and request.user == obj.author)