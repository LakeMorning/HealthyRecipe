from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from .forms import SignupForm
from django.contrib.auth import login, authenticate
import copy
import numpy as np
import csv
from decimal import Decimal

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
    # cursor.execute("UPDATE healthyrecipeapp_user SET height = 175 WHERE userName = 'chongluhehe'")
    
    # context = {
    #     # 'title': 'Test Jinja Template',
    #     'recipes': recipes
    # }
    
    return render(request, 'healthyrecipeapp/index.html', {'recipes': recipes})
    
def cart(request):
    cursor = connection.cursor()
    user_name = request.user.username
    # return HttpResponse(user_name)
    if(user_name is ''):
        # return HttpResponse('not logged in')
        return redirect('http://healthyrecipe.web.engr.illinois.edu:8001')
        
    # user_id = user_id[0][0]
    cursor.execute("SELECT healthyrecipeapp_user.id FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
    user_id = cursor.fetchall()[0][0]
    # cursor.execute("SELECT recipe_id FROM healthyrecipeapp_meal WHERE user_id = %s", [user_id])
    # recipe_ids = cursor.fetchall()
    cursor.execute("SELECT * FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id IN (SELECT healthyrecipeapp_meal.recipe_id FROM healthyrecipeapp_meal WHERE user_id = %s)", [user_id] )
    user_meal = cursor.fetchall()
    if(len(user_meal) == 0):
        return HttpResponse('Empty cart - You have not selected any dishes!')
        
    cursor.execute("SELECT SUM(DISTINCT calorie) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
    total_calorie = cursor.fetchall()[0][0]
    cursor.execute("SELECT SUM(DISTINCT prep_time) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
    total_prep_time = cursor.fetchall()[0][0]
    
    # recommendation
    # cursor.execute("SELECT healthyrecipeapp_review.user_id, healthyrecipeapp_review.recipe_id, healthyrecipeapp_review.rating FROM healthyrecipeapp_review, healthyrecipeapp_user WHERE healthyrecipeapp_review.user_id = healthyrecipeapp_user.id")
    # my_matrix = cursor.fetchall()
    # np.save('matrix', my_matrix)
   
    # my_matrix = np.load('matrix.npy')
    # lists = np.asarray(my_matrix,dtype = np.int32)
    # sparse = np.zeros((120, 100), dtype=np.int32)
    # for t in lists:
    #     sparse[t[0]-1,t[1]-1] = t[2]
    
    # all_scores = decompose(sparse, user_id - 1)
    
    Q = np.load('Q_matrix.npy')
    P = np.load('P_matrix.npy')
    all_scores = np.dot(Q[user_id - 1,:],P)
    # recommendation = all_scores.argsort()[-5:][::-1]
    cursor.execute("SELECT height, weight, age FROM healthyrecipeapp_user WHERE id = %s", [user_id])
    user_info = cursor.fetchall()

    target_calorie = 66 + ( 6.23 * user_info[0][1]) + (4.953 * user_info[0][0]) - (6.8 * user_info[0][2])

    predict = all_scores.argsort()[-30:][::-1]

    recommendations = []
    for i in range(0, len(predict)):
        cursor.execute("SELECT calorie FROM healthyrecipeapp_recipe WHERE id = %s", [predict[i] + 1])
        recipe_calorie = cursor.fetchall()
    
        nomorlized_calorie = target_calorie - float(total_calorie) - recipe_calorie[0][0]
        
        recommendations.append((abs(nomorlized_calorie), predict[i] + 1))
    recommendations = sorted(recommendations, key = lambda x:x[0], reverse = False)

    recommendation= []
    for i in range(5):
        recommendation.append(recommendations[i][1])
    recommendation_list = []
    for i in range(0, len(recommendation)):
        cursor.execute("(SELECT healthyrecipeapp_recipe.name, healthyrecipeapp_recipe.id FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id = %s)", [recommendation[i]])
        recommendation_list.append(cursor.fetchall()[0])
    # recommendation_list = cursor.fetchall()
    
    context = {
        'user_meal': user_meal,
        'total_calorie': total_calorie,
        'total_prep_time': total_prep_time,
        'recs': recommendation_list
    }
    
    transposed = list(zip(*user_meal))
    recipe_ids = transposed[0]
    button = request.GET.get('mybtn')
    if(button):
        # return HttpResponse(recipe_ids)
        ind = int(button)
        if(user_id is None):
            return redirect('http://healthyrecipe.web.engr.illinois.edu:8001')
        recipe_id = recipe_ids[ind - 1]
        # return HttpResponse(user_id)
        
        cursor.execute("DELETE FROM healthyrecipeapp_meal WHERE user_id = %s AND recipe_id = %s ",[user_id,recipe_id])
        
        cursor.execute("SELECT * FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id IN (SELECT healthyrecipeapp_meal.recipe_id FROM healthyrecipeapp_meal WHERE user_id = %s)", [user_id] )
        user_meal = cursor.fetchall()
        cursor.execute("SELECT SUM(DISTINCT calorie) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
        total_calorie = cursor.fetchall()[0][0]
        cursor.execute("SELECT SUM(DISTINCT prep_time) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
        total_prep_time = cursor.fetchall()[0][0]
        
        if(len(user_meal) == 0):
            return HttpResponse('Empty cart - You have not selected any dishes!')
        
        cursor.execute("SELECT height, weight, age FROM healthyrecipeapp_user WHERE id = %s", [user_id])
        user_info = cursor.fetchall()
    
        target_calorie = 66 + ( 6.23 * user_info[0][1]) + (4.953 * user_info[0][0]) - (6.8 * user_info[0][2])
    
        predict = all_scores.argsort()[-30:][::-1]
    
        recommendations = []
        for i in range(0, len(predict)):
            cursor.execute("SELECT calorie FROM healthyrecipeapp_recipe WHERE id = %s", [predict[i] + 1])
            recipe_calorie = cursor.fetchall()
        
            nomorlized_calorie = target_calorie - float(total_calorie) - recipe_calorie[0][0]
            
            recommendations.append((abs(nomorlized_calorie), predict[i] + 1))
        recommendations = sorted(recommendations, key = lambda x:x[0], reverse = False)
    
        recommendation= []
        for i in range(5):
            recommendation.append(recommendations[i][1])
        recommendation_list = []
        for i in range(0, len(recommendation)):
            cursor.execute("(SELECT healthyrecipeapp_recipe.name, healthyrecipeapp_recipe.id FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id = %s)", [recommendation[i]])
            recommendation_list.append(cursor.fetchall()[0])
            
    button1 = request.GET.get('mybn')
    if(button1):
        # return HttpResponse(recipe_ids)
        ind = int(button1)
        user_name = request.user.username
        # return HttpResponse(user_name)
        if(user_name is ''):
            return redirect('http://healthyrecipe.web.engr.illinois.edu:8001/login')
        # return HttpResponse(user_name)
        cursor.execute("SELECT healthyrecipeapp_user.id FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
        user_id = cursor.fetchall()[0][0]
        if(user_id is None):
            return redirect('http://healthyrecipe.web.engr.illinois.edu:8001')
        recipe_id = recommendation[ind - 1] + 1
        # return HttpResponse(user_id)
        cursor.execute("INSERT INTO healthyrecipeapp_meal(user_id, recipe_id) VALUES(%s,%s)",[user_id,recipe_id])
        cursor.execute("SELECT * FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id IN (SELECT healthyrecipeapp_meal.recipe_id FROM healthyrecipeapp_meal WHERE user_id = %s)", [user_id] )
        user_meal = cursor.fetchall()
        cursor.execute("SELECT SUM(DISTINCT calorie) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
        total_calorie = cursor.fetchall()[0][0]
        cursor.execute("SELECT SUM(DISTINCT prep_time) FROM healthyrecipeapp_meal,healthyrecipeapp_recipe WHERE user_id = %s AND recipe_id = healthyrecipeapp_recipe.id",[user_id])
        total_prep_time = cursor.fetchall()[0][0]
        
        if(len(user_meal) == 0):
            return HttpResponse('Empty cart - You have not selected any dishes!')
        
        cursor.execute("SELECT height, weight, age FROM healthyrecipeapp_user WHERE id = %s", [user_id])
        user_info = cursor.fetchall()
    
        target_calorie = 66 + ( 6.23 * user_info[0][1]) + (4.953 * user_info[0][0]) - (6.8 * user_info[0][2])
    
        predict = all_scores.argsort()[-30:][::-1]
    
        recommendations = []
        for i in range(0, len(predict)):
            cursor.execute("SELECT calorie FROM healthyrecipeapp_recipe WHERE id = %s", [predict[i] + 1])
            recipe_calorie = cursor.fetchall()
        
            nomorlized_calorie = target_calorie - float(total_calorie) - recipe_calorie[0][0]
            
            recommendations.append((abs(nomorlized_calorie), predict[i] + 1))
        recommendations = sorted(recommendations, key = lambda x:x[0], reverse = False)
    
        recommendation= []
        for i in range(5):
            recommendation.append(recommendations[i][1])
        recommendation_list = []
        for i in range(0, len(recommendation)):
            cursor.execute("(SELECT healthyrecipeapp_recipe.name, healthyrecipeapp_recipe.id FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id = %s)", [recommendation[i]])
            recommendation_list.append(cursor.fetchall()[0])
        
    context = {
        'user_meal': user_meal,
        'total_calorie': total_calorie,
        'total_prep_time': total_prep_time,
        'recs': recommendation_list
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
    recipess = cursor.fetchall()
    
    recipes = []
    for i in range(0, len(recipess)):
        recipes.append([recipess[i][0], recipess[i][1]])
    
    # ranking_recipes = copy.deepcopy(recipes)
    
    if(len(recipes) == 0):
        return HttpResponse("Oops...No corresponding food. We'll try to add it later!")
    
    # context = {
    #     'recipes': recipes
    # }
    #return render(request, 'healthyrecipeapp/sresult.html', context)
    
    
    #ranking
    cursor.execute("SELECT healthyrecipeapp_user.id FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[request.user.username])
    user_id = cursor.fetchall()[0][0]
    
    cursor.execute("SELECT healthyrecipeapp_review.user_id, healthyrecipeapp_review.recipe_id, healthyrecipeapp_review.rating FROM healthyrecipeapp_review, healthyrecipeapp_user WHERE healthyrecipeapp_review.user_id = healthyrecipeapp_user.id")
    my_matrix = cursor.fetchall()
    lists = np.asarray(my_matrix,dtype = np.int32)
    sparse = np.zeros((120, 100), dtype=np.int32)
    for t in lists:
        sparse[t[0]-1,t[1]-1] = t[2]
        
    ranking = user_based(sparse, user_id-1)
    
    scores = []
    
    for i in range(0,len(recipes)):
        cur_name = recipes[i][0]
        cur_id = recipes[i][1]
        score = ranking[cur_id-1]
        scores.append((score, cur_id, cur_name))
        
    scores = sorted(scores, key=lambda x:x[0], reverse=True)
    
    # return HttpResponse(scores)
    
    for i in range(0,len(recipes)):
        recipes[i][1] = scores[i][1]
        recipes[i][0] = scores[i][2]
    
    
    context = {
        'recipes': recipes
    }
        
    
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
        if(user_name is ''):
            return redirect('http://healthyrecipe.web.engr.illinois.edu:8001/login')
        # return HttpResponse(user_name)
        cursor.execute("SELECT healthyrecipeapp_user.id FROM healthyrecipeapp_user WHERE healthyrecipeapp_user.userName = %s",[user_name])
        user_id = cursor.fetchall()[0][0]
        if(user_id is None):
            return redirect('http://healthyrecipe.web.engr.illinois.edu:8001')
        recipe_id = recipe_ids[ind - 1]
        # return HttpResponse(user_id)
        cursor.execute("INSERT INTO healthyrecipeapp_meal(user_id, recipe_id) VALUES(%s,%s)",[user_id,recipe_id])
        
    # return render(request, 'healthyrecipeapp/meal.html, context)
        
        # return HttpResponse(recipes[1])
        
    return render(request, 'healthyrecipeapp/sresult.html', context)

def profile(request):
    cursor = connection.cursor()
    user_name = request.user.username
    
    if(user_name is ''):
        return redirect('http://healthyrecipe.web.engr.illinois.edu:8001')
    
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

    # key_word = request.GET.get('updateWeight', None)
    # if(key_word):
    #     newWeight = int(key_word)
    #     cursor.execute("UPDATE healthyrecipeapp_user SET healthyrecipeapp_user.weight = %s WHERE healthyrecipeapp_user.userName = %s",[newWeight, user_name])
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
            
            # return HttpResponse('Signup successful')
            return render(request, 'healthyrecipeapp/index.html')
        else:
            return HttpResponse('Signup failed')
    else:
        form = SignupForm()
    return render(request, 'healthyrecipeapp/signup.html', {'form': form})
    
    
def recipe_detail(request, id=id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM healthyrecipeapp_recipe WHERE healthyrecipeapp_recipe.id = %s", [id])
    recipe = cursor.fetchall()
    
    cursor.execute("SELECT healthyrecipeapp_review.rating, healthyrecipeapp_review.content, healthyrecipeapp_user.userName FROM healthyrecipeapp_review, healthyrecipeapp_user WHERE healthyrecipeapp_review.recipe_id = %s AND healthyrecipeapp_review.user_id = healthyrecipeapp_user.id", [id])
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
            return redirect('http://healthyrecipe.web.engr.illinois.edu:8001')
            
        recipe_id = id;
        
        cursor.execute("INSERT INTO healthyrecipeapp_review(user_id, recipe_id, rating, content) VALUES(%s,%s,%s,%s)",[user_id,recipe_id,rating,content])
        return redirect('http://healthyrecipe.web.engr.illinois.edu:8001/recipes/' + str(recipe_id))


def user_based(sparse,	goal_user):
	n_user,n_attrib = sparse.shape
	goal_attrib = 2
	epsilan = 1e-8
	#notice if a row or column is all zero, there will be a bug
	user_mean = np.sum(sparse, axis = 1)/np.sum(sparse != 0,axis = 1)
	# print('user_mean',user_mean)
	attrib_mean = np.mean(sparse, axis = 0)/np.sum(sparse != 0,axis = 0)
	# print('attrib_mean',attrib_mean)
	# print('attrib_mean',attrib_mean)
	mask = (sparse != 0)

	sparse_uzero_mean = sparse - np.reshape(user_mean,(-1,1))
	# sparse_azero_mean = sparse - np.reshape(attrib_mean,(1,-1))
	U = np.zeros((n_user,n_user))
	for i in range (0,sparse.shape[0]):
		for j in range(0,sparse.shape[0]):
			combined_mask = np.multiply(mask[i,:],mask[j,:])
			if(np.any(combined_mask)):
			#before nomalize
				U[i,j] = np.sum(np.multiply(np.multiply(sparse[i,:] - user_mean[i],\
											sparse[j,:] - user_mean[j])\
											,combined_mask))
				magnitudes = np.sqrt(\
							np.multiply(np.sum(np.multiply(np.square(sparse[i,:] - user_mean[i])\
											,combined_mask)),\
							np.sum(np.multiply(np.square(sparse[j,:] - user_mean[j])\
											,combined_mask)))\
							) + epsilan
				U[i,j] = U[i,j]/magnitudes
	# print('U',U[goal_user,:])

	predict = np.zeros((n_attrib),dtype = np.float32)
	for j in range(0,sparse.shape[1]):
		if sparse[goal_user,j] != 0:
			predict[j] = sparse[goal_user,j]
		else:
			# indi,indj = check_reverse(goal_user,j)
			predict[j] = attrib_mean[j] + np.dot(\
				np.multiply(sparse[:,j] != 0,sparse[:,j]-attrib_mean[j]),\
				U[goal_user,:])
	return predict

def decompose(sparse,goal_user):
	np.random.seed(21)
	latent_dim = 20
	height,width = sparse.shape
	lenda = 0.0001
	losses = []
	mask = sparse != 0
	# mask = np.ones(shape = sparse.shape,dtype = np.float32)
	# print np.multiply(mask,sparse+1)

	Q = np.random.normal(1,0.5,[height,latent_dim])
	P = np.random.normal(1,0.5,[latent_dim,width])
	loss = 1./2.*np.sum(np.multiply(mask,np.square(sparse-np.dot(Q,P)))) + 1./2.*lenda*(np.sum(np.square(Q)) + np.sum(np.square(P)))
	# print(np.dot(Q,P))
	P_losses = []
	Q_losses = []
	while(loss > 15):
		#optimize q
		# Q  = Q + alpha*(np.dot(np.multiply(mask,sparse-np.dot(Q,P.T)),P) + lenda*Q)
		# P  = P + alpha*(np.dot(np.multiply(mask,sparse-np.dot(Q,P.T)).T,Q) + lenda*P)
		for j in range(0,width):
			for d in range(0,latent_dim):
				upper_left = np.dot(Q[:,d],sparse[:,j])
				tem_mask = mask[:,j]
				# print upper_left

				cur_sum = 0
				for dp in range(0,latent_dim):
					if(dp != d):
						cur_sum += np.sum(np.multiply(tem_mask,np.multiply(np.multiply(P[dp,j],Q[:,dp]),Q[:,d])))
						# print 'cur_sum',cur_sum
				upper = upper_left - cur_sum

				down = np.sum(np.multiply(tem_mask,np.multiply(Q[:,d],Q[:,d]))) + lenda
				P[d,j] = upper/down
				# print('P[d,j]',P[d,j])
				loss = 1./2.*np.sum(np.multiply(mask,np.square(sparse-np.dot(Q,P)))) + 1./2.*lenda*(np.sum(np.square(Q)) + np.sum(np.square(P)))
				P_losses.append(loss)
				# print loss

		for i in range(0,height):
			for d in range(0,latent_dim):
				upper_left = np.dot(sparse[i,:],P[d,:])
				tem_mask = mask[i:i+1,:]
				cur_sum = 0
				for dp in range(0,latent_dim):
					if(dp != d):
						cur_sum += np.sum(np.multiply(tem_mask,np.multiply(np.multiply(Q[i,dp],P[dp,:]),P[d,:])))
				upper = upper_left - cur_sum
				down = np.sum(np.multiply(tem_mask,np.multiply(P[d,:],P[d,:]))) + lenda
				Q[i,d] = upper/down
				loss = 1./2.*np.sum(np.multiply(mask,np.square(sparse-np.dot(Q,P)))) + 1./2.*lenda*(np.sum(np.square(Q)) + np.sum(np.square(P)))
				Q_losses.append(loss)
				# print loss
		loss = 1./2.*np.sum(np.multiply(mask,np.square(sparse-np.dot(Q,P)))) + 1./2.*lenda*(np.sum(np.square(Q)) + np.sum(np.square(P)))
		print(loss)
	return np.dot(Q[goal_user,:],P)

















