from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Task(models.Model):
    new_status="new"
    in_progress_status="in_progress"
    done_status="done"
    CHOICE_STATUS=[
        (new_status,"New"),
        (in_progress_status,"In progress"),
        (done_status,"Completed"),
    ]

    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    deadline=models.DateTimeField()
    is_notified=models.BooleanField(default=False)
    status=models.CharField(max_length=20,choices=CHOICE_STATUS,default=new_status)
    created_at=models.DateTimeField(auto_now_add=True)
    user_owner=models.ForeignKey(User,on_delete=models.CASCADE)

    def overdue(self):
        return self.deadline<timezone.now() and self.status !=self.done_status
    def __str__(self):
        return self.title