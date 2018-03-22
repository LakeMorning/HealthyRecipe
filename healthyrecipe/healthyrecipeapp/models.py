'''
from django.db import models
from datetime import datetime

# Create your models here.
class Posts(models.Model):
  title = models.CharField(max_length=200)
  body = models.TextField()
  created_at = models.DateTimeField(default=datetime.now, blank=True)
  def __str__(self):
    return self.title
  class Meta:
    verbose_name_plural = "Posts"
'''

from django.db import models

# Create your models here.
class User(models.Model):
    userName = models.CharField(null=True, max_length=100)
    password = models.CharField(null=True, max_length=100)
    height = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(null=True, max_length=100)
    exerciseFreq =  models.IntegerField(null=True)

class Ingredient(models.Model):
    name = models.CharField(null=True, max_length=100)
    calorie = models.IntegerField(null=True)

class Recipe(models.Model):
    ingredients = models.ManyToManyField(Ingredient, through='Quantity')
    name = models.CharField(null=True, max_length=100)
    calorie = models.IntegerField(null=True)
    prep_time = models.IntegerField(null=True)
    direction = models.TextField(null=True)

class Quantity(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True)
    content = models.TextField(null=True)
