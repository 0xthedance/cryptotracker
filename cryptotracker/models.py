from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class CryptocurrencyPrice(models.Model):
    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=10)



class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    public_address = models.CharField(max_length=42, unique=True)

    def __str__(self):
        return f"{self.public_address}"
'''
class SnapshotAssets(models.Model):
    cryptocurrency = models.ForeignKey('Cryptocurrency', on_delete= models.CASCADE)
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    purchase_price = models.DecimalField(max_digits=20, decimal_places=2)
    purchase_date = models.DateField()

    def __str__(self):
        return f"{self.cryptocurrency} - {self.quantity}"
'''


