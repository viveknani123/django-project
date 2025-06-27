from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [

    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('userhome/', views.userhome, name='userhome'),
    path('graph/', views.graph, name='graph'),
    path('gallery/', views.gallery_view, name='gallery'),  # ✅ Change this
    path('train/', views.train, name='train'),
    path('predict/', views.predict, name='predict'),
    path('upload/', views.upload_image, name='upload_image'),
    path('uploaded-images/', views.uploaded_images, name='uploaded_images'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
