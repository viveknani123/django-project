from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Register, UploadedImage, PredictionModel, Gallery
from django.core.files.storage import FileSystemStorage
import os
import pickle
import numpy as np
from PIL import Image as PILImage  # Avoid name conflict with .models.Image

# Initialize model as None
model = None

# Try to load ML model from file if it exists and is valid
model_path = os.path.join(os.path.dirname(__file__), 'model', 'model.pkl')
try:
    if os.path.exists(model_path) and os.path.getsize(model_path) > 100:  # Basic check for non-empty file
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
    else:
        print(f"Warning: Model file not found or too small at {model_path}")
except Exception as e:
    print(f"Error loading model: {e}")

# ---------------------- INDEX ----------------------
def index(request):
    return render(request, 'index.html')

# ---------------------- ABOUT ----------------------
def about(request):
    return render(request, 'about.html')

# ---------------------- REGISTER ---------------------
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conpassword = request.POST.get('conpassword')
        age = request.POST.get('age')
        contact = request.POST.get('contact')

        if password != conpassword:
            return render(request, 'register.html', {'message': "Passwords don't match"})

        user = Register.objects.create(
            name=name, email=email, password=password,
            age=age, contact=contact
        )

        request.session['user_id'] = user.id
        return redirect('userhome')

    return render(request, 'register.html')

# ---------------------- LOGIN ----------------------
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Register.objects.get(email=email, password=password)
            request.session['user_id'] = user.id
            return redirect('userhome')
        except Register.DoesNotExist:
            return render(request, 'login.html', {'message': 'Invalid login'})

    return render(request, 'login.html')

# ---------------------- LOGOUT ----------------------
def logout(request):
    request.session.flush()
    return redirect('index')

# ---------------------- USER HOME ----------------------
def userhome(request):
    if 'user_id' not in request.session:
        return redirect('login')
    return render(request, 'userhome.html')

# ---------------------- IMAGE UPLOAD ----------------------
def upload_image(request):
    message = ""
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        UploadedImage.objects.create(image=filename)
        message = "Image uploaded successfully!"
    return render(request, 'upload_image.html', {'message': message})

# ---------------------- VIEW IMAGES ----------------------
def view(request):
    images = UploadedImage.objects.all()
    return render(request, 'view.html', {'images': images})

# ---------------------- GALLERY ----------------------
def gallery(request):
    galleries = Gallery.objects.all()
    return render(request, 'gallery.html', {'galleries': galleries})

# ---------------------- PREDICTION ----------------------
def prediction(request):
    if request.method == 'POST':
        if model is None:
            return render(request, 'prediction.html', {
                'error': 'Model not loaded. Please contact the administrator.'
            })
            
        try:
            image_file = request.FILES['image']
            
            # Process the image and make prediction
            img = PILImage.open(image_file)
            img = img.resize((224, 224))  # Adjust size as needed
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            prediction = model.predict(img_array)
            
            return render(request, 'prediction.html', {
                'prediction': prediction,
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

# ---------------------- MODULE TRAIN PAGE ----------------------
def module(request):
    return render(request, 'module.html')

# ---------------------- GRAPH VIEW ----------------------
def graph(request):
    predictions = PredictionModel.objects.all()
    return render(request, 'graph.html', {'predictions': predictions})
