import os
import pickle
import numpy as np
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Register, UploadedImage, Image, Gallery, PredictionRecord
from django.contrib.auth.models import User
from .models import PredictionRecord
# --- Load Model Once (good practice) ---
MODEL_PATH = os.path.join(settings.BASE_DIR, 'mainapp', 'model', 'model.pkl')
with open(MODEL_PATH, 'rb') as file:
    model = pickle.load(file)

# --- Home Page ---
def home(request):
    return render(request, 'index.html')

# --- About Page ---
def about(request):
    return render(request, 'about.html')

# --- User Home Page ---
@login_required
def userhome(request):
    return render(request, 'userhome.html')

# --- Register ---
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
        # Optionally create a profile in Register table
        Register.objects.create(name=username, email=email, password=password, age=age, contact=contact)

        messages.success(request, 'Registration Successful! Please login.')
        return redirect('login')

    return render(request, 'register.html')

# --- Login ---
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
            return redirect('login')
    return render(request, 'login.html')

# --- Logout ---
def logout_view(request):
    logout(request)
    return redirect('login')

# --- Upload Image ---
@login_required
def upload_image(request):
    if request.method == 'POST':
        uploaded_image = request.FILES['image']
        UploadedImage.objects.create(image=uploaded_image)
        messages.success(request, 'Image uploaded successfully!')
        return redirect('upload_image')
    return render(request, 'upload_image.html')

# --- Gallery ---
@login_required
def gallery_view(request):
    galleries = Image.objects.all()
    return render(request, 'gallery.html', {'galleries': galleries})

# --- Train Module (Dummy) ---
@login_required
def train(request):
    if request.method == 'POST':
        dataset = request.FILES.get('dataset')
        if not dataset:
            return render(request, 'train.html', {'error': 'Please upload a dataset file.'})
        if not dataset.name.endswith(('.csv', '.xlsx')):
            return render(request, 'train.html', {'error': 'Invalid file type. Upload CSV or XLSX only.'})

        save_path = os.path.join(settings.BASE_DIR, 'uploads', dataset.name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb+') as destination:
            for chunk in dataset.chunks():
                destination.write(chunk)
        # You can add training logic here
        return render(request, 'train.html', {'message': 'Training complete!'})
    return render(request, 'train.html')

@login_required
def predict(request):
    prediction = None
    feedback = []
    tips = []

    if request.method == 'POST':
        try:
            screen_time = float(request.POST.get('screen_time'))
            unlocks = int(request.POST.get('unlocks'))
            social_media = float(request.POST.get('social_media'))
            restless = int(request.POST.get('restless'))
            morning_check = int(request.POST.get('morning_check'))

            # Only allow positive values for time and unlocks
            if screen_time <= 0 or unlocks < 0 or social_media < 0:
                return render(request, 'predict.html', {'error': 'Screen time, unlocks, and social media must be positive numbers.'})

            input_data = np.array([[screen_time, social_media, restless, morning_check]])
            prediction_result = model.predict(input_data)
            if prediction_result[0] == 1:
                prediction = "High Risk of Mobile Addiction"
                feedback.append("You may need to reduce screen time.")
                tips.append("Set daily phone usage limits.")
            else:
                prediction = "Low Risk of Mobile Addiction"
                feedback.append("Your usage seems normal.")
                tips.append("Continue balanced phone usage.")

            PredictionRecord.objects.create(
                user=request.user,
                screen_time=screen_time,
                unlocks=unlocks,
                social_media=social_media,
                restless=bool(restless),
                morning_check=bool(morning_check),
                result=prediction
            )

            return redirect('graph')
        except Exception as e:
            return render(request, 'predict.html', {'error': str(e)})

    return render(request, 'predict.html', {
        'prediction': prediction,
        'feedback': feedback,
        'tips': tips
    })

from django.shortcuts import render
from .models import PredictionRecord
@login_required
def graph(request):
    # Get all predictions
    predictions = PredictionRecord.objects.all()
    # Prepare data for graph (example: screen_time and unlocks)
    screen_times = [p.screen_time for p in predictions]
    unlocks = [p.unlocks for p in predictions]
    return render(request, "graph.html", {
        "screen_times": screen_times,
        "unlocks": unlocks,
    })
@login_required
def history(request):
    records = PredictionRecord.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'records': records})


# --- Uploaded Images View (if you want to show uploaded images by user) ---
@login_required
def uploaded_images(request):
    images = UploadedImage.objects.all().order_by('-uploaded_at')
    return render(request, 'uploaded_images.html', {'images': images})

def create_prediction(request):
    if request.method == "POST":
        # Get data from form, here using example values
        pred = PredictionRecord.objects.create(
            user=request.user if request.user.is_authenticated else None,
            screen_time=200,
            unlocks=40,
            social_media=80,
            result="Low Risk of Mobile Addiction"
        )
        return redirect('graph')  # or wherever your graph page is
    return render(request, "create_prediction.html")
from django.shortcuts import render
from .models import PredictionRecord

def prediction_history_graph(request):
    # Example: show the last 10 predictions for the current user
    user = request.user
    records = PredictionRecord.objects.filter(user=user).order_by('-id')[:10][::-1]

    labels = [r.timestamp.strftime('%Y-%m-%d') for r in records]  # adjust the field as needed
    # Assume result is "High Risk of Mobile Addiction" or "Low Risk of Mobile Addiction"
    data = [1 if r.result == "High Risk of Mobile Addiction" else 0 for r in records]

    return render(request, "prediction_history_graph.html", {
        "labels": labels,
        "data": data,
    })