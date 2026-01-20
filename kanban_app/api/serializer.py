from django.contrib.auth.models import User
from rest_framework import serializers
from kanban_app.models import Boards, DashboardTasks, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]

class CheckMailSerializer(serializers.ModelSerializer):
    """
    Serializer to represent a user with:
    - ID
    - Email
    - Full name (first + last name)
    """
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id' ,'email','fullname']
    def get_fullname(self, obj):
        return obj.get_full_name()
    
class TasksSerializer(serializers.ModelSerializer):
    """
    Serializer for DashboardTasks model
    - Includes nested assignee and reviewer info
    - Includes count of comments
    - Supports write-only fields for assignee_id and reviewer_id
    """
    reviewer = CheckMailSerializer(source="reviewer_id", read_only=True)
    assignee = CheckMailSerializer(source="assignee_id", read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    board = serializers.PrimaryKeyRelatedField(queryset=Boards.objects.all())
    comments_count = serializers.SerializerMethodField()
   

    def get_comments_count(self, obj):
        return obj.comments.count()

    class Meta:
        model = DashboardTasks
        fields = ['id' ,'board' ,'title','description','status', 'priority','assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date', 'comments_count']

class TaskDetailSerializer(serializers.ModelSerializer):

    reviewer = CheckMailSerializer(source="reviewer_id", read_only=True)
    assignee = CheckMailSerializer(source="assignee_id", read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    class Meta:
        model = DashboardTasks
        fields = ['id' ,'title','description','status', 'priority','assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date']

class BoardsMixin(serializers.Serializer):
    """
    Serializer fields for additional board metrics
    - member_count: number of members in the board
    - ticket_count: total number of tasks
    - tasks_to_do_count: number of tasks with status 'To Do'
    - tasks_high_prio_count: number of high-priority tasks
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()
    
class OwnerIdMixin(serializers.Serializer):
    owner_id = serializers.ReadOnlyField(source="owner.id")

class BoardsSerializer(BoardsMixin,OwnerIdMixin, serializers.ModelSerializer):
    """
    Serializer for Boards model
    - Nested members (full user info)
    - Nested tasks (with TasksSerializer)
    - Allows assigning members via member_ids (write-only)
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = Boards
        fields = ['id' ,'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id', 'members']

    
class BoardDetailSerializer(OwnerIdMixin, serializers.ModelSerializer):
    """
    Serializer for detailed board representation.
    Includes:
    - Owner information (nested user data)
    - Members information (list of nested user data)
    """
    owner_data = CheckMailSerializer(source="owner", read_only=True)
    members_data = CheckMailSerializer(source="members", many=True, read_only=True)
    members = CheckMailSerializer(many=True, read_only=True)
    tasks = TasksSerializer(many=True,read_only=True)


    class Meta:
        model = Boards
        fields = ['id' ,'title','owner_id', 'members', 'owner_data','members_data', 'tasks']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request:
            if request.method == "PATCH":
                # Remove fields for PATCH requests
                self.fields.pop("owner_id", None)
                self.fields.pop("members", None)
                self.fields.pop("tasks", None)
            elif request.method == "GET":
                # Remove fields for GET requests
                self.fields.pop("owner_data", None)
                self.fields.pop("members_data", None)

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model
    - Shows author full name (read-only)
    - Created_at and author are read-only fields
    """
    author = serializers.CharField(
        source='author.get_full_name',
        read_only=True
    )
    class Meta:
        model = Comment
        fields = ['id','created_at', 'author', 'content']
        read_only_fields = ['created_at', 'author']

