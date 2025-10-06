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
@login_required(login_url="login")


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
    if form.is_valid():
        task=form.save(commit=False)
        task.user_owner=request.user
        task.save()
        return redirect("home")
    return render(request,"todo_folder/task_create.html",{"form":form})

def task_mark_done(request,pk):
    task=get_object_or_404(Task,pk=pk)
    task.status=Task.done_status
    task.save()
    return redirect('home')

@login_required
def update_task(request,pk):
    task=get_object_or_404(Task,pk=pk,user_owner=request.user)
    form=TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        return redirect("home")
    return render(request, "todo_folder/task_update.html",{"form":form})

@login_required
def delete_task(request,pk):
    task=get_object_or_404(Task,pk=pk,user_owner=request.user)
    if request.method =="POST":
        task.delete()
        return redirect("home")
    return render(request,"todo_folder/task_delete.html",{"task":task})

@login_required
@require_POST
def change_status(request,pk):
    task=get_object_or_404(Task,pk=pk,user_owner=request.user)
    status=request.POST.get("status")
    if status in dict(Task.choice_status).keys():
        task.status=status
        task.save()
    return redirect("home")


def send_task_reminder(task):
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

def reminder_deadline():
    now=timezone.now()
    one_hour_later=now+timedelta(hours=1)
    tasks=Task.objects.filter(
        deadline__range=(one_hour_later,one_hour_later+timedelta(minutes=1)),
        is_notified=False
    )
    
    for task in tasks:
        send_task_reminder(task)

def start_scheduler():
    scheduler=BackgroundScheduler()
    scheduler.add_job(reminder_deadline,'interval',minutes=1)
    scheduler.start()
    