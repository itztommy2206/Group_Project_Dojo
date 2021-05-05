from django.shortcuts import render, redirect, HttpResponse
from .models import * 
from django.contrib import messages
import bcrypt
import requests
from .forms import CityForm, ZipForm

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
    # zipForm = ZipForm()
    
    if request.method =="POST":
        form = CityForm(request.POST or None)
        # zipForm = ZipForm(request.POST)
        
        if form.is_valid():
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


            
            # new_zip = zipForm.cleaned_data['zipcode']
            # existing_zip_count = Zip.bojects.filter(zipcode = new_zip).count()
            # if existing_zip_count == 0:
            #     t = requests.get(url2.format(new_zip)).json()
            #     if t['cod'] == 200:
            #         for city in cities:
            #             if city.city != t['name']:
            #                 zipForm.save()
            #             else:
            #                 err_msg ="City already exist"
            # else:
            #     err_msg ="City already exists"

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
            "city": r['name'],
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
        # "zipForm":zipForm,
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

def zipcode(request):
    if 'user_id' not in request.session:
        return redirect('/')
    url2 = "http://api.openweathermap.org/data/2.5/weather?zip={}&units=imperial&appid=9daf36046d4eaa5f629f1a54d0892481" 
    zips = Zip.objects.all()
    zipcode_data = []
    for zipcode in zips:
        t = requests.get(url2.format(zipcode.zipcode)).json()
        zip_weather = {
            "city":t['name'],
            "temperature":t['main']['temp'],
            "description":t["weather"][0]["description"],
            "icon":t['weather'][0]['icon']
        }
        zipcode_data.append(zip_weather)
    error_messages = ""
    zipcodeForm = ZipForm()
    if request.method == "POST":
        zipcodeForm = ZipForm(request.POST or None)
        if zipcodeForm.is_valid():
            new_zip = zipcodeForm.cleaned_data['zipcode'] 
            existing_zip_count = Zip.objects.filter(zipcode = new_zip).count()
            if existing_zip_count == 0:
                t = requests.get(url2.format(new_zip)).json()
                if t['cod'] == 200:
                    if t['name'] != zip_weather.city:
                        
                        zipcodeForm.save()
                else:
                    error_messages = "This zipcode can't be pinpointed"
            else:
                error_messages = "Zipcode already exists"
   
   

    context ={
        "zipForm":zipcodeForm,
        "zipcode_weather":zipcode_data,
        "err_messages":error_messages

    }

    return render(request, "zipcode.html", context)
