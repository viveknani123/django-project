from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('userhome/', views.userhome, name='userhome'),
    path('prediction/', views.prediction, name='prediction'),
    path('graph/', views.graph, name='graph'),
]

