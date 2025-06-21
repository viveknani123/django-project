from django.db import models

class Register(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)
    age = models.CharField(max_length=50)
    contact = models.CharField(max_length=50, null=True, blank=True, default="Unknown")

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Image(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class PredictionModel(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    prediction_result = models.CharField(max_length=100)
    prediction_date = models.DateTimeField(auto_now_add=True)

class Gallery(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    images = models.ManyToManyField(Image)
