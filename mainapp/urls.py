from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('userhome/', views.userhome, name='userhome'),
    path('graph/', views.graph, name='graph'),
    path('gallery/', views.gallery, name='gallery'),
    path('train/', views.train, name='train'),
    path('predict/', views.predict, name='predict'),
    path('graph/', views.graph, name='graph'),
]