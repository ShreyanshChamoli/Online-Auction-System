from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class product(models.Model):
	product_name=models.CharField(max_length=300)
	product_description=models.TextField(null=True)
	min_bid=models.FloatField()
	valid_date=models.DateTimeField()
	category=models.CharField(max_length=300)	

class bids(models.Model):
	product=models.ForeignKey(product,on_delete=models.CASCADE)
	bid_amount=models.FloatField()
	user=models.ForeignKey(User,on_delete=models.CASCADE)
