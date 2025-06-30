from django.db import models
from django.contrib.auth.models import User

# --- Register Model (for user registration) ---
class Register(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=50)  # Consider using Django's User model for auth!
    age = models.CharField(max_length=50)
    contact = models.CharField(max_length=50, null=True, blank=True, default="Unknown")

    def __str__(self):
        return self.name

# --- For uploaded images (general uploads) ---
class UploadedImage(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name

# --- Image model for gallery system ---
class Image(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} - {self.title}"

# --- Gallery Model (for grouping images) ---
class Gallery(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    images = models.ManyToManyField(Image)

    def __str__(self):
        return self.name

# --- Prediction Record (use this for user predictions, history, and graphs) ---
class PredictionRecord(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    screen_time = models.FloatField()
    unlocks = models.IntegerField()
    social_media = models.FloatField()
    restless = models.BooleanField()
    morning_check = models.BooleanField()
    result = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.result} ({self.created_at:%Y-%m-%d %H:%M})"