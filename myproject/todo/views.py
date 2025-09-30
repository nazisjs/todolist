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