from django.contrib import admin
from .models import Register, UploadedImage, Image, PredictionModel, Gallery

admin.site.register(Register)
admin.site.register(UploadedImage)
admin.site.register(Image)
admin.site.register(PredictionModel)
admin.site.register(Gallery)