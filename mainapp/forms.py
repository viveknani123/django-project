from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
from django import forms
from .models import Image

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'image']
