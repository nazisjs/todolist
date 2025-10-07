from .forms import CreateUserForm
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm
from django.utils import timezone
from django.views.decorators.http import require_POST
from .filters import TaskFilter
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form=CreateUserForm()
        if request.method=="POST":
            form=CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user=form.cleaned_data.get('username')
            messages.success(request,'Account was created for '+ user)
            return redirect('login')

    context={'form':form}
    return render(request,'todo_folder/register.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method=="POST":
            username=request.POST.get("username")
            password=request.POST.get("password")
            user=authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                messages.info(request,"Username OR Password is incorrect!")
                
        context={}
        return render(request,'todo_folder/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')
    
class TaskManager:
    def __init__(self,user):
        self.user=user
    def get_tasks(self):
        return Task.objects.filter(user_owner=self.user).order_by("deadline")
    def create(self,form):
        task=form.save(commit=False)
        task.user_owner=self.user
        task.save()
        return task
    def update(self,task,form):
        form.save()
        return task
    def delete(self,task):
        task.delete()
    def mark_done(self,task):
        task.status=Task.done_status
        task.save()
    def change_status(self,task,status):
        if status in dict(Task.choice_status).keys():
            task.status=status
            task.save()

@login_required
def home(request):
    tasks=Task.objects.filter(user_owner=request.user).order_by("deadline") 
    myfilter=TaskFilter(request.GET,queryset=tasks)
    tasks=myfilter.qs

    now=timezone.now()
    for task in tasks:
        if task.deadline<now:
            task.deadline_status="overdue"
        elif task.deadline-now <= timedelta(hours=24):
            task.deadline_status="soon"
        else:
            task.deadline_status="normal"
    return render(request,"todo_folder/home.html",{"tasks":tasks, "choice_status": Task.CHOICE_STATUS,"myfilter":myfilter,})

@login_required
def create_task(request):
    form=TaskForm(request.POST or None)
    manager=TaskManager(request.user)
    if form.is_valid():
        manager.create(form)
        return redirect("home")
    return render(request,"todo_folder/task_create.html",{"form":form})

@login_required
def change_status(request,pk):
    manager=TaskManager(request.user)
    task=get_object_or_404(Task,pk=pk,user_owner=request.user)
    manager.change_status(task,request.POST.get("status"))
    return redirect("home")

@login_required
def task_mark_done(request, pk):
    manager = TaskManager(request.user)
    task = get_object_or_404(Task, pk=pk, user_owner=request.user)
    manager.mark_done(task)
    return redirect("home")

@login_required
def update_task(request, pk):
    manager = TaskManager(request.user)
    task = get_object_or_404(Task, pk=pk, user_owner=request.user)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        manager.update(task, form)
        return redirect("home")
    return render(request, "todo_folder/task_update.html", {"form": form})

@login_required
def delete_task(request, pk):
    manager=TaskManager(request.user)
    task=get_object_or_404(Task, pk=pk, user_owner=request.user)
    if request.method == "POST":
        manager.delete(task)
        return redirect("home")
    return render(request, "todo_folder/task_delete.html", {"task": task})


class ReminderEmail:
    def __init__(self):
        self.scheduler=BackgroundScheduler()

    def send_task_reminder(self,task):
        if task.user_owner.email:
            send_mail(
                "Reminder from Task Tracker!",
                f"Hi {task.user_owner.username}! "
                f"1 hour left until your deadline: {task.title}. You better hurry up!",
            settings.EMAIL_HOST_USER,
            [task.user_owner.email],
            fail_silently=False
        )
        task.is_notified=True
        task.save()
        
    def reminder_deadline(self):
        now=timezone.now()
        one_hour_later=now+timedelta(hours=1)
        tasks=Task.objects.filter(
        deadline__range=(one_hour_later,one_hour_later+timedelta(minutes=1)),is_notified=False)
        for task in tasks:
            self.send_task_reminder(task)

    def start_scheduler(self):
        self.scheduler.add_job(self.reminder_deadline,'interval',minutes=1)
        self.scheduler.start()

