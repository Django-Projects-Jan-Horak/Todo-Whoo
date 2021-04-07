from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .models import Todo
from .forms import TodoForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, "todo/home.html")

def signupuser(request):
    if request.method == "GET":
        return render(request, "todo/signupuser.html", {'form': UserCreationForm()})
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(request.POST['username'],None, request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, "todo/signupuser.html", {'form': UserCreationForm(), 'error':"This username has been already taken"})

        else:
            return render(request, "todo/signupuser.html", {'form': UserCreationForm(), 'error':"Passwords did not match"})

@login_required   
def currenttodos(request):
    #todos = Todo.objects.all()
    todos = Todo.objects.filter(user = request.user, completed_date__isnull=True)
    todos.reverse()
    return render(request, "todo/currenttodos.html", {"todos":todos, "user" : request.user})

@login_required
def logoutuser(request):
    if request.method == "POST":
        logout(request)        
        return redirect("home")

def loginuser(request):
    if request.method == "GET":
        return render(request, "todo/loginuser.html", {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username = request.POST["username"], password= request.POST["password"])
        if user is None:
            return render(request, "todo/loginuser.html", {'form':AuthenticationForm(), "error":"Username & password did not match"})
        else:
            login(request, user)
            return redirect("home")

@login_required
def createtodo(request):
    if request.method == "GET":
        return render(request, "todo/createtodo.html", {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit = False)
            newtodo.user = request.user
            newtodo.save()
            return redirect("currenttodos")
        except ValueError:
            return render(request, "todo/createtodo.html", {'form':TodoForm(), "error":"Something went wrong"})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk = todo_pk, user = request.user)
    if request.method == "GET":
        form = TodoForm(instance=todo)
        return render(request, "todo/viewtodo.html", {'form':form, "todo":todo})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect("currenttodos")
        except ValueError:
            return render(request, "todo/viewtodo.html", {'form':TodoForm(), "error":"Form error..."})

@login_required
def completetodo(request, todo_pk):
   # if request.method == "POST":
    todo = get_object_or_404(Todo, pk = todo_pk, user = request.user)
    todo.completed_date = timezone.now()
    todo.save()
    return redirect("currenttodos")

@login_required
def deletetodo(request, todo_pk):
    if request.method == "POST":
        todo = get_object_or_404(Todo, pk = todo_pk, user = request.user)
        todo.delete()
    return redirect("currenttodos")

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user = request.user, completed_date__isnull=False)
    todos.reverse()
    return render(request, "todo/completedtodos.html", {"todos":todos, "user" : request.user})

@login_required
def markasuncopleted(request, todo_pk):
    if request.method == "POST":
        todo = get_object_or_404(Todo, pk = todo_pk, user = request.user)
        todo.completed_date = None
        todo.save()
        return redirect("currenttodos")
