from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  

class Subscribers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriber = models.CharField(max_length=255)

    def __str__(self):
        return self.subscriber

class qr_code(models.Model):
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    name = models.CharField(max_length=50)
    size = models.IntegerField()
    shape = models.IntegerField()
    custom_style = models.CharField(max_length=255)
    link = models.TextField()
    data_create = models.DateTimeField(default=timezone.now)
    expiry_date = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name    