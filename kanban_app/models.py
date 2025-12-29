from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Boards(models.Model):
    board_title = models.CharField(max_length=150)
    board_members = models.ManyToManyField(User)
    created_date = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.board_title
    
# choices (db_value, display_value)
class TaskPriority(models.Model):
    task_status = models.CharField(
        max_length=6,
        choices=[
            ("low", "low priority"),
            ("medium", "medium priority"),
            ("high", "high priority")
        ],
        default= "low"
    )
    

class DashboardTasks(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    assigned = models.ForeignKey(User, related_name="assigned_tasks", on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(User, related_name="reviewed_tasks", on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.ForeignKey(TaskPriority, on_delete=models.PROTECT)

    def __str__(self):
        return self.title