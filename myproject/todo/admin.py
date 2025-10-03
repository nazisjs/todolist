from django.contrib import admin
from .models import Task
# Register your models here.
class TaskAdmin(admin.ModelAdmin):
    list_display=("title","description","deadline","status","created_at","user_owner")
admin.site.register(Task,TaskAdmin)