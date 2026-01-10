from django.contrib.auth.models import User
from rest_framework import serializers
from kanban_app.models import Boards, DashboardTasks, Comment

class CheckMailSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id' ,'email','fullname']
    def get_fullname(self, obj):
        return obj.get_full_name()
    
class TasksSerializer(serializers.ModelSerializer):
    assignee = CheckMailSerializer(source='assignee_id', read_only=True)
    reviewer = CheckMailSerializer(source='reviewer_id', read_only=True)
    comments_count = serializers.SerializerMethodField()

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )
    def get_comments_count(self, obj):
        return obj.comments.count()

    class Meta:
        model = DashboardTasks
        fields = ['id' ,'title','description', 'board', 'assignee', 'reviewer', 'due_date', 'priority', 'status', 'comments_count','assignee_id', 'reviewer_id']

class BoardsSerializer(serializers.ModelSerializer):
    members = CheckMailSerializer(read_only = True, many=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        source='members',
        write_only=True
    )
    tasks = TasksSerializer(read_only=True, many=True)
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Boards
        fields = ['id' ,'title', 'created_date', 'members', 'member_ids', 'member_count', 'ticket_count', 'tasks', 'tasks_to_do_count', 'tasks_high_prio_count']

    def to_internal_value(self, data):
        if 'members' in data and 'member_ids' not in data:
            data['member_ids'] = data.pop('members')
        return super().to_internal_value(data)
    
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(
        source='author.get_full_name',
        read_only=True
    )
    class Meta:
        model = Comment
        fields = ['id', 'task', 'content', 'created_at', 'author']
        read_only_fields = ['created_at', 'author']

