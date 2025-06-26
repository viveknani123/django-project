from django.shortcuts import render, redirect

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def login_view(request):
    return render(request, 'login.html')

def logout_view(request):
    return redirect('login')  # Or implement Django logout logic

def register(request):
    return render(request, 'register.html')

def userhome(request):
    return render(request, 'userhome.html')

def graph(request):
    return render(request, 'graph.html')

def gallery(request):
    return render(request, 'gallery.html')

def train(request):
    return render(request, 'train.html')

def predict(request):
    return render(request, 'predict.html')
