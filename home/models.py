from django.db import models
from django.contrib.auth.models import User

class Subscribers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriber = models.CharField(max_length=255)

class qr_code(models.Model):
    image = models.ImageField(upload_to="images/")
    name = models.CharField(max_length=50)
    size = models.IntegerField()
    shape = models.IntegerField()
    custom_style = models.CharField(max_length=255)
    link = models.TextField()
    data_create = models.IntegerField()
    expiry_date = models.IntegerField()