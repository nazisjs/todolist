from .forms import CreateUserForm
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

def registerPage(request):
    form=CreateUserForm()
    if request.method=="POST":
        form=CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

    context={'form':form}
    return render(request,'todo_folder/register.html',context)

def loginPage(request):
    return render(request,'todo_folder/login.html')