from django.contrib import admin
from .models import Boards, DashboardTasks, Comment
# Register your models here.

class BoardsAdmin(admin.ModelAdmin):
    """
    Admin interface for Boards model
    - Display 'title' field in list view
    """
    list_display=["title"]

class DashboardTasksAdmin(admin.ModelAdmin):
    """
    Admin interface for DashboardTasks model
    - Display 'title' field in list view
    """
    list_display=["title"]

class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model
    - Display 'content' field in list view
    """
    list_display=["content"]

admin.site.register(Boards, BoardsAdmin)
admin.site.register(DashboardTasks, DashboardTasksAdmin)
admin.site.register(Comment, CommentAdmin)
