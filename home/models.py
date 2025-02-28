from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)
    shape = models.IntegerField(null=True, blank=True)
    custom_style = models.CharField(max_length=255, null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    data_create = models.DateTimeField(default=timezone.now, null=True, blank=True)
    expiry_date = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name or "Пуста ячейка"