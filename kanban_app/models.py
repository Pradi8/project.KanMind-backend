from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Boards(models.Model):
    """
    Represents a Kanban board.
    - title: Name of the board
    - members: Users associated with this board (ManyToMany)
    - created_date: Date when the board was created
    """
    title = models.CharField(max_length=150)
    members = models.ManyToManyField(User)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
class DashboardTasks(models.Model):
    """
    Represents a task in the Kanban system.
    Fields:
    - title: Short title of the task
    - description: Detailed description
    - board: Related Board (nullable)
    - assignee_id: User assigned to complete the task
    - reviewer_id: User reviewing the task
    - due_date: Optional deadline
    - priority: Task priority (low, medium, high)
    - status: Task status (to-do, in-progress, review, done)
    """
    PRIORITY_CHOICES = [
        ("low", "low priority"),
        ("medium", "medium priority"),
        ("high", "high priority"),
    ]

    STATUS_CHOICES = [
        ("to-do", "to-do"),
        ("in-progress", "in-progress"),
        ("review", "review"),
        ("done", "done"),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField()
    board =  models.ForeignKey(Boards, related_name="tasks", null=True, blank=True, on_delete=models.SET_NULL)
    assignee_id = models.ForeignKey(User, related_name="assigned_tasks", on_delete=models.SET_NULL, null=True, blank=True)
    reviewer_id = models.ForeignKey(User, related_name="reviewed_tasks", on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default="medium")
    status =  models.CharField(max_length=15, choices=STATUS_CHOICES, default="to-do")

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    """
    Represents a comment on a task.
    Fields:
    - task: The related task (nullable)
    - content: Text of the comment (max 300 chars)
    - created_at: Timestamp when comment was created
    - author: User who wrote the comment
    """
    task = models.ForeignKey(DashboardTasks, related_name="comments", null=True, blank=True, on_delete=models.SET_NULL)
    content = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE) 

    def __str__(self):
        return self.content[:50]