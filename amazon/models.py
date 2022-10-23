from django.db import models
import uuid
import json
# Create your models here.


class User(models.Model):
    username = models.TextField(blank=False, max_length=30)
    gmail = models.TextField(blank=False)
    password = models.TextField(blank=False, max_length=100)
    orders = models.TextField(default=json.dumps([]))
    cart = models.TextField(default=json.dumps([]))


class Product(models.Model):
    prod_id = models.IntegerField(default=1)
    prod_img = models.TextField(blank=False)
    title = models.CharField(blank=False, max_length=100)
    desc = models.TextField()
    stock = models.IntegerField(default=10)
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=100)
