from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('sresult', views.sresult, name = 'sresult'), 
    path('cart', views.cart, name = 'cart'),
    path('profile', views.profile, name = 'profile'),
    path('login', auth_views.login, name='login'),
    path('logout', auth_views.logout, {'next_page': '/'}, name='logout'),
    path('recipes/<int:id>', views.recipe_detail, name='recipe_detail'),
    path('recipes/<int:id>/comments/new', views.new_comment, name='new_comment'),
    path('recipes/<int:id>/comments', views.comment_detail, name='comment_detail'),
]