# from django.shortcuts import render
# from django.http import HttpResponse
# from django.db import connection
import csv
import os

# Create your views here.
def insert_data(cursor):
    #return HttpResponse('HELLO THERE')
    with open('recipe.csv', 'r') as f:
        reader = csv.reader(f)
        recipe_list = list(reader)

    with open('quantity.csv', 'r') as f:
        reader = csv.reader(f)
        contain_list = list(reader)

    with open('ingredient.csv', 'r') as f:
        reader = csv.reader(f)
        ingredient_list = list(reader)    
    recipe_list[0][0] = recipe_list[0][0][1:]
    contain_list[0][0] = contain_list[0][0][1:]
    ingredient_list[0][0] = ingredient_list[0][0][1:]

    def convert2sentence(list_,types, name):
    #get header:
        header_string = ','.join(str(h) for h in list_[0])
        start_string = 'INSERT INTO ' + name + '('
        middle_string = ') VALUES('
        end_string = ')'
        first_part = start_string + header_string + middle_string
        ret = []
        if(len(types) != len(list_[0])):
            print('types dimension wrong')
        for i in range(1, len(list_)):
            tuple_str = ''
            for j in range(0,len(list_[i])):
                if(types[j] == 'string'):
                    tuple_str = ','.join([tuple_str,"\'"+ str(list_[i][j])+"\'"])
                else:
                    tuple_str = ','.join([tuple_str,str(list_[i][j])])
            tuple_str = tuple_str[1:]
            ful_string = first_part + tuple_str + end_string
            ret.append(ful_string)
        return ret
        # cursor.execute("INSERT INTO healthyrecipeapp_user(userName, password, height, weight, age, gender, exerciseFreq) VALUES('cl', '123', 180, 165, 23, 'male', 5)")
    recipe_type = ['string','string','int','string','string']
    contain_type = ['int', 'int', 'string']
    ingredient_type = ['string', 'int']

    recipe_exe = convert2sentence(recipe_list, recipe_type, 'Recipe')
    contain_exe = convert2sentence(contain_list, contain_type, 'Quantity')
    ingredient_exe = convert2sentence(ingredient_list, ingredient_type, 'Ingredient')

    # cursor = connection.cursor()

    for i in range(0,len(recipe_exe)):
        cursor.execute(recipe_exe[i])

    for i in range(0,len(contain_exe)):
        cursor.execute(contain_exe[i])
        
    for i in range(0,len(ingredient_exe)):
        cursor.execute(ingredient_exe[i])
    # print (ingredient_exe)
    return
    # #insert
    # # cursor.execute("INSERT INTO healthyrecipeapp_user(userName, password, height, weight, age, gender, exerciseFreq) VALUES('cl', '123', 180, 165, 23, 'male', 5)")
insert_data()    
    # #select
    # cursor.execute("SELECT * FROM healthyrecipeapp_user")
    # testUsers = cursor.fetchall()
    
    # #delete
    
    # context = {
    #     'title': 'Test Jinja Template',
    #     'users': testUsers
    # }
    
    # return render(request, 'healthyrecipeapp/index.html', context)