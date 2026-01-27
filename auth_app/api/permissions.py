from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrMemberBoard(BasePermission):
    """
    Object-level permission for Board access.
    - User must be authenticated (handled by IsAuthenticated)
    - User must be owner or member of the board
    """

    def has_permission(self, request, view):
        # Only allow authenticated users to pass.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Object-level check AFTER board is loaded (404 already handled)
        user = request.user
        return obj.owner == user or user in obj.members.all()

class IsBoardMemberForTask(BasePermission):
    #Only Board owner or Board members can access the Task
    def has_permission(self, request, view):
        # Only allow authenticated users to pass.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not obj.board:
            return False  
        user = request.user
        return obj.board.owner == user or user in obj.board.members.all() 

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
        
        # GET/POST → board members or owner
        if request.method in SAFE_METHODS:
            if not obj.task or not obj.task.board:
                return False  # Task or Board missing → deny
            board = obj.task.board
            return user == board.owner or user in board.members.all()

        # Edit/Delete → only comment author
        return user == obj.author