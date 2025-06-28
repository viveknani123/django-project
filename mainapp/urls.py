from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('userhome/', views.userhome, name='userhome'),

    # Features
    path('graph/', views.graph, name='graph'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('train/', views.train, name='train'),
    path('predict/', views.predict, name='predict'),
    path('history/', views.history, name='history'),

    # Image Upload
    path('upload/', views.upload_image, name='upload_image'),
    path('uploaded-images/', views.uploaded_images, name='uploaded_images'),
]

# For serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
