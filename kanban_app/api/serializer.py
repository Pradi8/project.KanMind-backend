from django.contrib.auth.models import User
from rest_framework import serializers
from kanban_app.models import Boards

class CheckMailSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id' ,'email','fullname']
    def get_fullname(self, obj):
        return obj.get_full_name()
    
class BoardsSerializer(serializers.ModelSerializer):
    board_members = serializers.PrimaryKeyRelatedField(
    many=True,
    queryset=User.objects.all()
)
    class Meta:
        model = Boards
        fields = ['id' ,'board_title', 'created_date', 'board_members']
