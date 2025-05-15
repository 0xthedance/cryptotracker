from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Network(models.Model):
    name = models.CharField(max_length=20)
    url_rpc = models.CharField(max_length=200, blank=True, null=True)
    image = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Cryptocurrency(models.Model):
    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=10)
    image = models.CharField(max_length=200)


class CryptocurrencyNetwork(models.Model):
    cryptocurrency = models.ForeignKey("Cryptocurrency", on_delete=models.CASCADE)
    network = models.ForeignKey("Network", on_delete=models.CASCADE)
    address = models.CharField(max_length=42)

    def __str__(self):
        return f"{self.cryptocurrency.name} on {self.network.name} ({self.address})"


class CryptocurrencyPrice(models.Model):
    cryptocurrency = models.ForeignKey("Cryptocurrency", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.cryptocurrency.name} - {self.price} - {self.date}"


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}"


class Address(models.Model):
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
    account = models.ForeignKey("Account", on_delete=models.CASCADE)
    wallet_type = models.CharField(
        max_length=20, choices=WALLET_TYPE_CHOICES, default=HOT
    )
    name = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.public_address}"


class SnapshotAssets(models.Model):
    cryptocurrency = models.ForeignKey(
        "CryptocurrencyNetwork", on_delete=models.CASCADE
    )
    address = models.ForeignKey("Address", on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    snapshot_date = models.DateTimeField()

    def __str__(self):
        return f"{self.cryptocurrency.name} - {self.quantity} - {self.snapshot_date}"


class SnapshotETHValidator(models.Model):
    address = models.ForeignKey("Address", on_delete=models.CASCADE)
    validator_index = models.IntegerField()
    public_key = models.CharField(max_length=128)
    balance = models.DecimalField(max_digits=20, decimal_places=5)
    status = models.CharField(max_length=20)
    activation_epoch = models.CharField()
    rewards = models.DecimalField(max_digits=20, decimal_places=5)
    snapshot_date = models.DateTimeField()

    def __str__(self):
        return f"{self.validator_index} - {self.balance}"


class Protocol(models.Model):
    name = models.CharField(max_length=20)
    network = models.ForeignKey("Network", on_delete=models.CASCADE)


class Pool(models.Model):
    name = models.CharField(max_length=20)
    protocol = models.ForeignKey("Protocol", on_delete=models.CASCADE)
    address = models.CharField(max_length=42)
    image = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} - {self.protocol}"


class PoolBalance(models.Model):
    pool = models.ForeignKey("Pool", on_delete=models.CASCADE)
    token = models.ForeignKey("Cryptocurrency", on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    snapshot_date = models.DateTimeField()

    def __str__(self):
        return f"{self.pool.name} - {self.quantity} - {self.snapshot_date}"


class PoolRewards(models.Model):
    pool = models.ForeignKey("Pool", on_delete=models.CASCADE)
    token = models.ForeignKey("Cryptocurrency", on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    snapshot_date = models.DateTimeField()

    def __str__(self):
        return f"{self.pool.name} - {self.quantity} - {self.snapshot_date}"


class SnapshotDate(models.Model):
    date = models.DateTimeField()
    address = models.ForeignKey("Address", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} - {self.address}"
