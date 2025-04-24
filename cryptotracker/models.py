from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Cryptocurrency(models.Model):
    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=10)
    image = models.CharField(max_length=200)
    address = models.CharField(max_length=42, unique=True)


class CryptocurrencyPrice(models.Model):
    cryptocurrency = models.ForeignKey("Cryptocurrency", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.cryptocurrency.name} - {self.price} - {self.date}"


class Account(models.Model):
    COLD = "COLD"
    HOT = "HOT"
    SMART = "SMART"

    WALLET_TYPE_CHOICES = [
        (COLD, "Cold"),
        (HOT, "Hot"),
        (SMART, "Smart"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    public_address = models.CharField(max_length=42, unique=True)
    wallet_type = models.CharField(
        max_length=20, choices=WALLET_TYPE_CHOICES, default=HOT
    )
    name = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.public_address}"


class SnapshotAssets(models.Model):
    cryptocurrency = models.ForeignKey("Cryptocurrency", on_delete=models.CASCADE)
    account = models.ForeignKey("Account", on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    snapshot_date = models.DateTimeField()

    def __str__(self):
        return f"{self.cryptocurrency.name} - {self.quantity} - {self.snapshot_date}"


class SnapshotETHValidator(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE)
    validator_index = models.IntegerField()
    public_key = models.CharField(max_length=128)
    balance = models.DecimalField(max_digits=20, decimal_places=5)
    status = models.CharField(max_length=20)
    activation_epoch = models.CharField()
    rewards = models.DecimalField(max_digits=20, decimal_places=5)
    snapshot_date = models.DateTimeField()

    def __str__(self):
        return f"{self.validator_index} - {self.balance}"


class SnapshotDate(models.Model):
    date = models.DateTimeField()
    account = models.ForeignKey("Account", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} - {self.account}"
