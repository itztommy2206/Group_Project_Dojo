from django.shortcuts import render, redirect, HttpResponse
from .models import * 
from django.contrib import messages
import bcrypt

## Register & Login
def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        errors = User.objects.reg_validator(request.POST)
        if errors:
            for value in errors.values():
                messages.error(request, value)
            return redirect('/')

        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            password = hashed_pw
        )
        request.session['user_id'] = user.id
        return redirect('/weather')
    return redirect('/')

def login(request):
    if request.method == "POST":
        user = User.objects.filter(email=request.POST['email'])
        if user:
            user = user[0]      
            if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
                request.session['user_id'] = user.id
                return redirect('/weather')
        messages.error(request, "Email or password is incorrect")
    return redirect('/')
    

def weather(request):
    if 'user_id' not in request.session:
        return redirect('/')
        
    context = {
        'current_user': User.objects.get(id=request.session['user_id']),
        'all_users': User.objects.all(),
    }
    return render(request, "weather_app.html", context)

def logout(request):
    request.session.flush()
    return redirect('/')