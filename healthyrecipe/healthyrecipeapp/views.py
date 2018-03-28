from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from .forms import SignupForm
from django.contrib.auth import login, authenticate

# Create your views here.
def index(request):
    #return HttpResponse('HELLO THERE')
    button = request.GET.get('cart')
    if(button):
        return cart(request)
    
    key_word = request.GET.get('search_box', None)
    if(key_word):
        request.session['key_word'] = key_word
        return sresult(request)
        
        
    cursor = connection.cursor()
    
    # insert
    # cursor.execute("INSERT INTO healthyrecipeapp_user(userName, password, height, weight, age, gender, exerciseFreq) VALUES('cl', '123', 180, 165, 23, 'male', 5)")
    
    # select
    cursor.execute("SELECT * FROM healthyrecipeapp_recipe")
    recipes = cursor.fetchall()
    
    # delete
    
    # update
    cursor.execute("UPDATE healthyrecipeapp_user SET height = 175 WHERE userName = 'chongluhehe'")
    
    context = {
        'title': 'Test Jinja Template',
        'recipes': recipes
    }
    
    return render(request, 'healthyrecipeapp/index.html', context)
    
def cart(request):
    cursor = connection.cursor()
    user_name = request.user.username
    cursor.execute("SELECT healthyrecipeapp_user.id FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
    user_id = cursor.fetchall()[0][0]
    if(user_id is None):
        return HttpResponse('not logged in')
    # cursor.execute("SELECT recipe_id FROM healthyrecipeapp_meal WHERE user_id = %s", [user_id])
    # recipe_ids = cursor.fetchall()
    cursor.execute("SELECT * FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id IN (SELECT healthyrecipeapp_meal.recipe_id FROM healthyrecipeapp_meal WHERE user_id = %s)", [user_id] )
    user_meal = cursor.fetchall()
    cursor.execute("SELECT SUM(calorie) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
    total_calorie = cursor.fetchall()[0][0]
    cursor.execute("SELECT SUM(prep_time) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
    total_prep_time = cursor.fetchall()[0][0]
    context = {
        'user_meal': user_meal,
        'total_calorie': total_calorie
        'total_prep_time': total_prep_time
    }
    
    transposed = list(zip(*user_meal))
    recipe_ids = transposed[0]
    button = request.GET.get('mybtn')
    if(button):
        # return HttpResponse(recipe_ids)
        ind = int(button)
        if(user_id is None):
            return HttpResponse('not logged in')
        recipe_id = recipe_ids[ind - 1]
        # return HttpResponse(user_id)
        
        cursor.execute("DELETE FROM healthyrecipeapp_meal WHERE user_id = %s AND recipe_id = %s ",[user_id,recipe_id])
        
        cursor.execute("SELECT * FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id IN (SELECT healthyrecipeapp_meal.recipe_id FROM healthyrecipeapp_meal WHERE user_id = %s)", [user_id] )
        user_meal = cursor.fetchall()
        cursor.execute("SELECT SUM(calorie) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
        total_calorie = cursor.fetchall()[0][0]
        cursor.execute("SELECT SUM(prep_time) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
        total_prep_time = cursor.fetchall()[0][0]
        context = {
            'user_meal': user_meal,
            'total_calorie': total_calorie
            'total_prep_time': total_prep_time
        }
    
    return render(request, 'healthyrecipeapp/cart.html', context)

def sresult(request):
    key_word = request.session['key_word']  
    okey_word = key_word
    key_word = '%' + key_word + '%'
    cursor = connection.cursor()
    # return HttpResponse(key_word) 
    cursor.execute("SELECT DISTINCT healthyrecipeapp_recipe.name, healthyrecipeapp_recipe.id FROM healthyrecipeapp_ingredient,healthyrecipeapp_recipe,healthyrecipeapp_quantity WHERE healthyrecipeapp_recipe.name Like %s OR (healthyrecipeapp_ingredient.name = %s AND healthyrecipeapp_quantity.recipe_id = healthyrecipeapp_recipe.id AND healthyrecipeapp_quantity.ingredient_id = healthyrecipeapp_ingredient.id) GROUP BY healthyrecipeapp_recipe.prep_time", [key_word,okey_word])
    recipes = cursor.fetchall()
    recipes = list(zip(*recipes))
    names = []
    for i in range (0,len(recipes[0])):
        names.append((recipes[0][i]))
    names = tuple(names)
    # return HttpResponse(names)
    
    context = {
        'recipes': names
    }
    recipe_ids = recipes[1]

    button = request.GET.get('mybtn')
    if(button):
        # return HttpResponse(recipe_ids)
        ind = int(button)
        user_name = request.user.username
        # return HttpResponse(user_name)
        cursor.execute("SELECT healthyrecipeapp_user.id FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
        user_id = cursor.fetchall()[0][0]
        if(user_id is None):
            return HttpResponse('not logged in')
        recipe_id = recipe_ids[ind - 1]
        # return HttpResponse(user_id)
        cursor.execute("INSERT INTO healthyrecipeapp_meal(user_id, recipe_id) VALUES(%s,%s)",[user_id,recipe_id])
        
    # return render(request, 'healthyrecipeapp/meal.html, context)
        
        # return HttpResponse(recipes[1])
        
    return render(request, 'healthyrecipeapp/sresult.html', context)

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






















