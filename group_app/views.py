from django.shortcuts import render, redirect, HttpResponse
from .models import * 
from django.contrib import messages
import bcrypt
import requests
from .forms import CityForm

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
    
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=9daf36046d4eaa5f629f1a54d0892481'
    err_msg = ""
    message = ""
    message_class =""

    if request.method =="POST":
        form = CityForm(request.POST)
        
        print(form)
        if form.is_valid():
            print(request.POST['city'])
            new_city = form.cleaned_data['city']
            existing_city_count = City.objects.filter(city = new_city, users = User.objects.get(id = request.session['user_id'])).count()
           
            if existing_city_count == 0:
                r = requests.get(url.format(new_city)).json()
                
                if r['cod'] == 200:
                    
                    form.save()
                    city_saved = City.objects.last()
                    connect_city_update_user = User.objects.get(id=request.session['user_id'])
                    connect_city_update_user.cities.add(city_saved)
                    connect_city_update_user.save()
                else:
                    err_msg = "City does not exist"
            else:
                err_msg = 'city already exists!'
        
        if err_msg:
            message = err_msg
            message_class = "is-danger"
        else:
            message = "City added successfully"
            message_class = "is-success"
    form = CityForm()
    cities = City.objects.filter(users = request.session['user_id']).order_by("city")
   
    weather_data =[]
    for city in cities:

        r = requests.get(url.format(city.city)).json()

        city_weather = {
            "city": city.city,
            "temperature": r['main']['temp'],
            "description":r["weather"][0]["description"],
            "icon":r["weather"][0]['icon']
        }
        weather_data.append(city_weather)
    
    city_belong_user = City.objects.filter(users = User.objects.get(id= request.session['user_id']))
    context = {
        'current_user': User.objects.get(id=request.session['user_id']),
        "current_user_city": city_belong_user,
        'all_users': User.objects.all(),
        'city_weather':weather_data,
        "form":form,
        "message":message,
        "message_class":message_class

    }

    
    return render(request, "weather_app.html", context)

def delete_city(request, city_name):
    if 'user_id' not in request.session:
        return redirect('/')
    City.objects.get(city = city_name, users = request.session['user_id']).delete()
    return redirect("weather")


def logout(request):
    request.session.flush()
    return redirect('/')