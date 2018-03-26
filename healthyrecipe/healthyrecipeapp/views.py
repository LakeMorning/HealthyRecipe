from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from .forms import SignupForm
from django.contrib.auth import login, authenticate

# Create your views here.
def index(request):
    #return HttpResponse('HELLO THERE')
    
    cursor = connection.cursor()
    
    # insert
    # cursor.execute("INSERT INTO healthyrecipeapp_user(userName, password, height, weight, age, gender, exerciseFreq) VALUES('cl', '123', 180, 165, 23, 'male', 5)")
    
    # select
    cursor.execute("SELECT * FROM healthyrecipeapp_recipe")
    recipes = cursor.fetchall()
    
    # delete
    
    context = {
        'title': 'Test Jinja Template',
        'recipes': recipes
    }
    
    return render(request, 'healthyrecipeapp/index.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # return HttpResponse(form.cleaned_data['userName'])
            
            form.save()
            
            userName = form.cleaned_data['username']
            raw_password = form.cleaned_data['password1']
            height = form.cleaned_data['height']
            weight = form.cleaned_data['weight']
            age = form.cleaned_data['age']
            gender = form.cleaned_data['gender']
            exerciseFreq = form.cleaned_data['exerciseFreq']
            
            user = authenticate(username=userName, password=raw_password)
            login(request, user)
            
            #save to database
            cursor = connection.cursor()
            cursor.execute("INSERT INTO healthyrecipeapp_user(userName, password, height, weight, age, gender, exerciseFreq) VALUES(%s, %s, %s, %s, %s, %s, %s)", [userName, raw_password, height, weight, age, gender, exerciseFreq])
            
            return HttpResponse('Signup successful')
        else:
            return HttpResponse('Signup failed')
    else:
        form = SignupForm()
    return render(request, 'healthyrecipeapp/signup.html', {'form': form})






















