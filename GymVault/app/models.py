from django.db import models
from django.contrib.auth.models import User


class Supplement_Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Equipment_Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)



class Supplement(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField()
    category = models.ForeignKey(Supplement_Category, on_delete=models.CASCADE)
    flavor = models.CharField(max_length=255, null=True,blank=True)
    img = models.FileField()



class Equipment(models.Model):

    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField()
    category = models.ForeignKey(Equipment_Category, on_delete=models.CASCADE)
    material = models.CharField(max_length=255, null=True, blank=True)
    img = models.FileField()

class Stock(models.Model):
    supplement = models.ForeignKey(Supplement, on_delete=models.CASCADE, null=True,blank=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True,blank=True)
    stock = models.PositiveIntegerField()
    weight = models.CharField(max_length=10, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,)

class Cart(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)  # Link to the Stock model
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User
    qty = models.PositiveIntegerField()
    total_price = models.IntegerField(null=True)

class Buy(models.Model):
    product = models.ForeignKey(Stock, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    address = models.TextField()  
    phone_number = models.CharField(max_length=15)

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)