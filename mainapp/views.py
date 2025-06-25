from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_protect
from .models import Register, UploadedImage, PredictionModel, Gallery
from django.db import IntegrityError
import os
import pickle
import numpy as np
from PIL import Image as PILImage

# Load ML model at startup (if exists)
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
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conpassword = request.POST.get('conpassword')
        age = request.POST.get('age')
        contact = request.POST.get('contact')

        if password != conpassword:
            messages.error(request, "Passwords don't match")
            return render(request, 'register.html')

        if Register.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'register.html')

        try:
            user = Register.objects.create(
                name=name,
                email=email,
                password=password,  # For real security, hash the password!
                age=age,
                contact=contact,
            )
            request.session['user_id'] = user.id
            messages.success(request, "Registration successful!")
            return redirect('userhome')
        except IntegrityError:
            messages.error(request, "Registration failed due to a database error")
        except Exception as e:
            messages.error(request, f"Registration failed: {e}")

    return render(request, 'register.html')

@csrf_protect
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = Register.objects.get(email=email, password=password)
            request.session['user_id'] = user.id
            messages.success(request, "Login successful!")
            return redirect('userhome')
        except Register.DoesNotExist:
            messages.error(request, 'Invalid email or password')

    return render(request, 'login.html')

def logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect('index')

def userhome(request):
    if 'user_id' not in request.session:
        return redirect('login')
    return render(request, 'userhome.html')

@csrf_protect
def upload_image(request):
    if 'user_id' not in request.session:
        return redirect('login')
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
    return render(request, 'upload_image.html')

def view(request):
    if 'user_id' not in request.session:
        return redirect('login')
    images = UploadedImage.objects.all()
    return render(request, 'view.html', {'images': images})

def gallery(request):
    if 'user_id' not in request.session:
        return redirect('login')
    galleries = Gallery.objects.all()
    return render(request, 'gallery.html', {'galleries': galleries})

@csrf_protect
def prediction(request):
    if 'user_id' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        if model is None:
            return render(request, 'prediction.html', {
                'error': 'Model not loaded. Please contact the administrator.',
                'model_loaded': False
            })
        try:
            image_file = request.FILES['image']
            img = PILImage.open(image_file)
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            pred_val = model.predict(img_array)
            pred_result = getattr(pred_val, 'tolist', lambda: pred_val)()
            return render(request, 'prediction.html', {
                'prediction': pred_result,
                'model_loaded': True
            })
        except Exception as e:
            return render(request, 'prediction.html', {
                'error': f'Error processing image: {str(e)}',
                'model_loaded': model is not None
            })
    return render(request, 'prediction.html', {
        'model_loaded': model is not None
    })

def module(request):
    if 'user_id' not in request.session:
        return redirect('login')
    return render(request, 'module.html')

def graph(request):
    if 'user_id' not in request.session:
        return redirect('login')
    predictions = PredictionModel.objects.all()
    return render(request, 'graph.html', {'predictions': predictions})