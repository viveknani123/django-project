import os
import joblib
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Register, UploadedImage, Image, Gallery, PredictionRecord
from django.core.files.storage import FileSystemStorage
import pickle
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import joblib
import os
import numpy as np
import pickle
import os
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import PredictionRecord
from django.conf import settings

BASE_DIR = settings.BASE_DIR
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load Model
model_path = os.path.join('mainapp', 'model', 'model.pkl')
with open(model_path, 'rb') as file:
    model = pickle.load(file)


# Home Page
def home(request):
    return render(request, 'index.html')

# About Page
def about(request):
    return render(request, 'about.html')
# User Home Page
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def userhome(request):
    return render(request, 'userhome.html')
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Register

from django.contrib.auth.models import User

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Register

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conpassword = request.POST.get('conpassword')
        age = request.POST.get('age')
        contact = request.POST.get('contact')

        if password != conpassword:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        # Create Django User
        user = User.objects.create_user(username=username, email=email, password=password)

        # Save to custom Register table
        Register.objects.create(name=username, email=email, password=password, age=age, contact=contact)

        messages.success(request, 'Registration Successful! Please login.')
        return redirect('login')

    return render(request, 'register.html')

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            if user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('userhome')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')  # 🔥 Important to stay on same page on failure

    return render(request, 'login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Upload Image
@login_required
def upload_image(request):
    if request.method == 'POST':
        uploaded_image = request.FILES['image']
        UploadedImage.objects.create(image=uploaded_image)
        messages.success(request, 'Image uploaded successfully!')
        return redirect('upload_image')
    return render(request, 'upload_image.html')

# Gallery
@login_required
def gallery_view(request):
    galleries = Image.objects.all()
    return render(request, 'gallery.html', {'galleries': galleries})

# Train Module
@login_required
def train(request):
    if request.method == 'POST':
        dataset = request.FILES.get('dataset')

        if not dataset:
            return render(request, 'train.html', {'error': 'Please upload a dataset file.'})

        if not dataset.name.endswith(('.csv', '.xlsx')):
            return render(request, 'train.html', {'error': 'Invalid file type. Upload CSV or XLSX only.'})

        save_path = os.path.join('uploads', dataset.name)
        with open(save_path, 'wb+') as destination:
            for chunk in dataset.chunks():
                destination.write(chunk)

        return render(request, 'train.html', {'message': 'Training complete!'})

    return render(request, 'train.html')

# Prediction
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import numpy as np
import pickle
import os
from .models import PredictionRecord
from django.conf import settings

@login_required
def predict(request):
    prediction = None
    feedback = []
    tips = []

    if request.method == 'POST':
        try:
            screen_time = request.POST.get('screen_time')
            unlocks = request.POST.get('unlocks')
            social_media = request.POST.get('social_media')
            restless = request.POST.get('restless')
            morning_check = request.POST.get('morning_check')

            if not all([screen_time, unlocks, social_media, restless, morning_check]):
                return render(request, 'predict.html', {'error': 'Please fill all the fields.'})

            screen_time = float(screen_time)
            unlocks = int(unlocks)
            social_media = float(social_media)
            restless = int(restless)
            morning_check = int(morning_check)

            input_data = np.array([[screen_time, social_media, restless, morning_check]])

            model_path = os.path.join(settings.BASE_DIR, 'mainapp', 'model', 'model.pkl')
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            prediction_result = model.predict(input_data)

            if prediction_result[0] == 1:
                prediction = "High Risk of Mobile Addiction"
                feedback.append("You may need to reduce screen time.")
                feedback.append("Try to limit social media usage.")
                tips.append("Set daily phone usage limits.")
                tips.append("Engage in offline activities like sports or reading.")
            else:
                prediction = "Low Risk of Mobile Addiction"
                feedback.append("Your usage seems normal.")
                tips.append("Continue maintaining a balanced phone usage.")

            # Save prediction history
            PredictionRecord.objects.create(
                user=request.user,
                screen_time=screen_time,
                unlocks=unlocks,
                social_media=social_media,
                restless=bool(restless),
                morning_check=bool(morning_check),
                result=prediction
            )

        except Exception as e:
            return render(request, 'predict.html', {'error': str(e)})

    return render(request, 'predict.html', {
        'prediction': prediction,
        'feedback': feedback,
        'tips': tips
    })


    

@login_required
def history(request):
    records = PredictionRecord.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'records': records})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PredictionRecord

@login_required
def graph(request):
    records = PredictionRecord.objects.filter(user=request.user).order_by('created_at')

    if not records.exists():
        return render(request, 'graph.html', {'labels': [], 'data': []})

    labels = [record.created_at.strftime('%Y-%m-%d %H:%M:%S') for record in records]
    data = [1 if "High" in record.result else 0 for record in records]

    return render(request, 'graph.html', {'labels': labels, 'data': data})

from django.contrib.auth.decorators import login_required
from .models import UploadedImage
from django.shortcuts import render

@login_required
def uploaded_images(request):
    images = UploadedImage.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'uploaded_images.html', {'images': images})
