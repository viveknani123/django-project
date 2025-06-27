from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UploadedImage, PredictionModel, Gallery, PredictionRecord, Image
from .forms import ImageUploadForm
import os
import pickle
import json

# Load ML model at startup
model = None
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')
if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 100:
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print(f"Warning: Model not found or is too small at {MODEL_PATH}")


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


@csrf_protect
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conpassword = request.POST.get('conpassword')

        if password != conpassword:
            messages.error(request, "Passwords don't match")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Registration successful! You can now login.")
        return redirect('login')

    return render(request, 'register.html')


@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('userhome')  # Prevent redirect loop

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.is_superuser:
                return redirect('/admin/')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('userhome')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')


@login_required
def userhome(request):
    return render(request, 'userhome.html')


@login_required
@csrf_protect
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        if not image.content_type.startswith('image/'):
            messages.error(request, 'Please upload a valid image file.')
            return render(request, 'upload_image.html')

        filename = get_random_string(8) + '_' + image.name
        fs = FileSystemStorage()
        saved_name = fs.save(filename, image)
        UploadedImage.objects.create(image=saved_name)

        messages.success(request, "Image uploaded successfully!")
        return redirect('uploaded_images')

    return render(request, 'upload_image.html')


@login_required
def uploaded_images(request):
    images = UploadedImage.objects.all().order_by('-uploaded_at')
    return render(request, 'uploaded_images.html', {'images': images})


@login_required
def gallery_view(request):
    galleries = Gallery.objects.all()
    return render(request, 'gallery.html', {'galleries': galleries})


@login_required
@csrf_protect
def predict(request):
    prediction = None
    error = None
    feedback = []
    tips = []
    if request.method == 'POST':
        try:
            screen_time = float(request.POST.get('screen_time'))
            unlocks = int(request.POST.get('unlocks'))
            social_media = float(request.POST.get('social_media'))
            restless = int(request.POST.get('restless'))
            morning_check = int(request.POST.get('morning_check'))

            features = [[screen_time, unlocks, social_media, restless, morning_check]]
            prediction_num = model.predict(features)[0]

            if screen_time > 5:
                feedback.append("Your screen time is high. Try to limit daily usage.")
            if unlocks > 50:
                feedback.append("Frequent phone unlocking detected.")
            if social_media > 3:
                feedback.append("A lot of time spent on social media apps.")
            if restless:
                feedback.append("You feel restless without your phone.")
            if morning_check:
                feedback.append("Checking your phone first thing in the morning is a sign of dependency.")

            tips = [
                "Set daily app usage limits.",
                "Leave your phone outside the bedroom at night.",
                "Schedule phone-free activities.",
                "Try digital detox days."
            ]

            if prediction_num == 2:
                prediction = "You are at HIGH risk of mobile addiction."
            elif prediction_num == 1:
                prediction = "You show MODERATE signs of mobile addiction."
            else:
                prediction = "You have a LOW risk of mobile addiction."

            PredictionRecord.objects.create(
                user=request.user if request.user.is_authenticated else None,
                screen_time=screen_time,
                unlocks=unlocks,
                social_media=social_media,
                restless=bool(restless),
                morning_check=bool(morning_check),
                result=prediction
            )

        except Exception as e:
            error = f"Invalid input: {str(e)}"

    return render(request, 'predict.html', {
        'prediction': prediction,
        'error': error,
        'feedback': feedback,
        'tips': tips,
    })


@login_required
def graph(request):
    records = PredictionRecord.objects.filter(user=request.user).order_by('created_at')
    labels = [record.created_at.strftime("%Y-%m-%d %H:%M") for record in records]

    data = []
    for record in records:
        if "HIGH" in record.result:
            data.append(2)
        elif "MODERATE" in record.result:
            data.append(1)
        else:
            data.append(0)

    return render(request, 'graph.html', {
        'labels': json.dumps(labels),
        'data': json.dumps(data)
    })


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
