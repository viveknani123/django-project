from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Register, UploadedImage, PredictionModel, Gallery
from django.core.files.storage import FileSystemStorage
import os
import pickle
import numpy as np
from PIL import Image as PILImage  # Avoid name conflict with .models.Image

# Load ML model from file
model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
with open(model_path, 'rb') as file:
    model = pickle.load(file)

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
    prediction_result = None
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']

        # Preprocess image
        img = PILImage.open(image_file).convert('L').resize((64, 64))  # grayscale, resize
        data = np.array(img).flatten().reshape(1, -1)  # shape: (1, 4096)

        # Predict
        result = model.predict(data)[0]
        prediction_result = f"Prediction: {result}"

    return render(request, 'prediction.html', {'prediction': prediction_result})

# ---------------------- MODULE TRAIN PAGE ----------------------
def module(request):
    return render(request, 'module.html')

# ---------------------- GRAPH VIEW ----------------------
def graph(request):
    predictions = PredictionModel.objects.all()
    return render(request, 'graph.html', {'predictions': predictions})
