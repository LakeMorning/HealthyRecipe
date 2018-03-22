from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection

# Create your views here.
def index(request):
    #return HttpResponse('HELLO THERE')
    
    cursor = connection.cursor()
    
    #insert
    # cursor.execute("INSERT INTO healthyrecipeapp_user(userName, password, height, weight, age, gender, exerciseFreq) VALUES('cl', '123', 180, 165, 23, 'male', 5)")
    
    #select
    cursor.execute("SELECT * FROM healthyrecipeapp_user")
    testUsers = cursor.fetchall()
    
    #delete
    
    context = {
        'title': 'Test Jinja Template',
        'users': testUsers
    }
    
    return render(request, 'healthyrecipeapp/index.html', context)