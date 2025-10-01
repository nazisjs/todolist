from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Task

class CreateUserForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','email','password1','password2']

class TaskForm(forms.ModelForm):
    class Meta: 
        model=Task
        fields=["title","description","deadline","status"]
        widget={
            "deadline":forms.DateTimeInput(attrs={"type":"datetime-local"}),
            }