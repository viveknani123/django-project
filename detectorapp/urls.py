from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),                # Home Page
    path('about/', views.about, name='about'),         # About Page
    path('login/', views.login_view, name='login'),    # Login Page
    path('logout/', views.logout_view, name='logout'), # Logout
    path('register/', views.register, name='register'),# Registration
    path('userhome/', views.userhome, name='userhome'),# User Home
    path('graph/', views.graph, name='graph'),         # Graph Page
    path('gallery/', views.gallery_view, name='gallery_view'),
    path('train/', views.train, name='train'),         # Model Training
    path('predict/', views.predict, name='predict'),   # Prediction Page
]
