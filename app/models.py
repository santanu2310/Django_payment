from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Product(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=5,decimal_places=2)
    description = models.CharField(max_length=500)
    image = models.ImageField(upload_to='images')
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name
    
    def get_image(self):
        if self.image:
            return settings.CURRENT_DOMAIN+self.image.url

PAYMENT_STATUS = [
    ('PENDING','PENDING'),
    ('AWAITING','AWAITING'),
    ('SUCCESSFUL','SUCCESSFUL')
]

class Order(models.Model):
    id = models.UUIDField(primary_key=True, editable= False, default=uuid.uuid4)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ])
    total_price = models.DecimalField(max_digits=6,decimal_places=2,blank=True, null=True)
    stripe_payment_id = models.CharField(max_length=200,blank=True, null=True)
    payment_status = models.CharField(max_length=10,choices=PAYMENT_STATUS,default=PAYMENT_STATUS[0][0])
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.product.name