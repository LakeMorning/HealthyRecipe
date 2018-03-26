from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    height = forms.IntegerField(label='height', required=True, help_text='centimeters')
    weight = forms.IntegerField(label='weight', required=True, help_text='pounds')
    age = forms.IntegerField(label='age', required=True)
    gender = forms.CharField(label='gender', required=True, max_length=100, help_text='m or f')
    exerciseFreq = forms.IntegerField(label='exerciseFreq', required=True, help_text='times/week')
    
    class Meta:
        model = User
        fields = ('height', 'weight', 'age', 'gender', 'exerciseFreq', 'username', 'password1', 'password2')
    