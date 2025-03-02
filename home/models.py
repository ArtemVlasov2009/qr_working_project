from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  
import time

class Subscribers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriber = models.CharField(max_length=255)
    qr_code_count = models.IntegerField(default=0)  
    plan = models.CharField(max_length=10, default='free')
    qr_code_limit = models.IntegerField(default=10)  
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.subscriber

class qr_code(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(max_length=2000, default='http://127.0.0.1:8000/')  
    size = models.IntegerField(default=300)
    shape = models.IntegerField(default=0)  
    custom_style = models.CharField(max_length=50, default="default")
    data_create = models.DateTimeField(default=timezone.now, null=False)
    expiry_date = models.FloatField(default=time.time)  
    image = models.CharField(max_length=500, null=True, blank=True)
    plan_created = models.CharField(max_length=50, default="free")

    def __str__(self):
        return self.name or "Unnamed QR Code"