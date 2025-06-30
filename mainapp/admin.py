from django.contrib import admin
from .models import Register, UploadedImage, Image, Gallery
from .models import PredictionRecord

admin.site.register(PredictionRecord)
admin.site.register(Register)
admin.site.register(UploadedImage)
admin.site.register(Image)
admin.site.register(Gallery)
