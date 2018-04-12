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
        
    button = request.GET.get('profile')
    if(button):
        return profile(request)
    
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
    # return HttpResponse(user_name)
    if(user_name is ''):
        return HttpResponse('not logged in')
        
    # user_id = user_id[0][0]
    cursor.execute("SELECT healthyrecipeapp_user.id FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
    user_id = cursor.fetchall()[0][0]
    # cursor.execute("SELECT recipe_id FROM healthyrecipeapp_meal WHERE user_id = %s", [user_id])
    # recipe_ids = cursor.fetchall()
    cursor.execute("SELECT * FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id IN (SELECT healthyrecipeapp_meal.recipe_id FROM healthyrecipeapp_meal WHERE user_id = %s)", [user_id] )
    user_meal = cursor.fetchall()
    if(len(user_meal) == 0):
        return HttpResponse('Empty cart! Please begin selecting your meals!')
    cursor.execute("SELECT SUM(calorie) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
    total_calorie = cursor.fetchall()[0][0]
    cursor.execute("SELECT SUM(prep_time) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
    total_prep_time = cursor.fetchall()[0][0]
    context = {
        'user_meal': user_meal,
        'total_calorie': total_calorie,
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
            'total_calorie': total_calorie,
            'total_prep_time': total_prep_time
        }
    
    return render(request, 'healthyrecipeapp/cart.html', context)

def sresult(request):
    key_word = request.session['key_word']  
    okey_word = key_word
    key_word = '%' + key_word + '%'
    cursor = connection.cursor()
    # return HttpResponse(key_word) 
    # cursor.execute("SELECT DISTINCT healthyrecipeapp_recipe.name, healthyrecipeapp_recipe.id FROM healthyrecipeapp_ingredient,healthyrecipeapp_recipe,healthyrecipeapp_quantity WHERE healthyrecipeapp_recipe.name Like %s OR (healthyrecipeapp_ingredient.name = %s AND healthyrecipeapp_quantity.recipe_id = healthyrecipeapp_recipe.id AND healthyrecipeapp_quantity.ingredient_id = healthyrecipeapp_ingredient.id) GROUP BY healthyrecipeapp_recipe.prep_time", [key_word,okey_word])
    cursor.execute("(SELECT healthyrecipeapp_recipe.name, healthyrecipeapp_recipe.id FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.name Like %s) UNION (SELECT healthyrecipeapp_recipe.name, healthyrecipeapp_recipe.id FROM healthyrecipeapp_ingredient,healthyrecipeapp_recipe,healthyrecipeapp_quantity WHERE healthyrecipeapp_ingredient.name = %s AND healthyrecipeapp_quantity.recipe_id = healthyrecipeapp_recipe.id AND healthyrecipeapp_quantity.ingredient_id = healthyrecipeapp_ingredient.id)", [key_word,okey_word])
    recipes = cursor.fetchall()
    
    if(len(recipes) == 0):
        return HttpResponse("Oops...No corresponding food. We'll try to add it later!")
    
    context = {
        'recipes': recipes
    }
    #return render(request, 'healthyrecipeapp/sresult.html', context)
    
    recipes = list(zip(*recipes))
    names = []
    for i in range (0,len(recipes[0])):
        names.append((recipes[0][i]))
    names = tuple(names)
    
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

def profile(request):
    cursor = connection.cursor()
    user_name = request.user.username
    cursor.execute("SELECT healthyrecipeapp_user.height FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
    height = cursor.fetchall()[0][0]
    cursor.execute("SELECT healthyrecipeapp_user.weight FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
    weight = cursor.fetchall()[0][0]
    cursor.execute("SELECT healthyrecipeapp_user.age FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
    age = cursor.fetchall()[0][0]
    cursor.execute("SELECT healthyrecipeapp_user.exerciseFreq FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
    exerciseFreq = cursor.fetchall()[0][0]
    context = {
        'height': height,
        'weight': weight,
        'age': age,
        'exerciseFreq': exerciseFreq
    }

    key_word = request.GET.get('updateWeight', None)
    if(key_word):
        newWeight = int(key_word)
        cursor.execute("UPDATE healthyrecipeapp_user SET healthyrecipeapp_user.weight = %s WHERE healthyrecipeapp_user.userName = %s",[newWeight, user_name])
    return render(request, 'healthyrecipeapp/profile.html', context)

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
    
    
def recipe_detail(request, id=id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id = %s", [id])
    recipe = cursor.fetchall()
    
    cursor.execute("SELECT healthyrecipeapp_review.rating, healthyrecipeapp_review.content FROM healthyrecipeapp_review WHERE healthyrecipeapp_review.recipe_id = %s", [id])
    comments = cursor.fetchall()
    
    context = {
        'recipes': recipe,
        'comments': comments
    }
    
    return render(request, 'healthyrecipeapp/show.html', context)

def new_comment(request, id=id):
    # return HttpResponse('new comment...')
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id = %s", [id])
    recipe = cursor.fetchall()
    return render(request, 'healthyrecipeapp/comment.html', {'recipe': recipe})

def comment_detail(request, id=id):
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        content = request.POST.get('content')
        
        user_name = request.user.username
        # return HttpResponse(user_name)
        cursor = connection.cursor()
        cursor.execute("SELECT healthyrecipeapp_user.id FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
        user_id = cursor.fetchall()[0][0]
        if(user_id is None):
            return HttpResponse('not logged in')
            
        recipe_id = id;
        
        cursor.execute("INSERT INTO healthyrecipeapp_review(user_id, recipe_id, rating, content) VALUES(%s,%s,%s,%s)",[user_id,recipe_id,rating,content])
        return redirect('http://healthyrecipe.web.engr.illinois.edu:8001/recipes/' + str(recipe_id))





















