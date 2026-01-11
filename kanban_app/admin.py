from django.contrib import admin
from .models import Boards, DashboardTasks, Comment
# Register your models here.

class BoardsAdmin(admin.ModelAdmin):
    list_display=["title"]

class DashboardTasksAdmin(admin.ModelAdmin):
    list_display=["title"]

class CommentAdmin(admin.ModelAdmin):
    list_display=["content"]

admin.site.register(Boards, BoardsAdmin)
admin.site.register(DashboardTasks, DashboardTasksAdmin)
admin.site.register(Comment, CommentAdmin)
