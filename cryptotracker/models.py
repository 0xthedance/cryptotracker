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

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class CryptocurrencyNetwork(models.Model):
    cryptocurrency = models.ForeignKey("Cryptocurrency", on_delete=models.CASCADE)
    network = models.ForeignKey("Network", on_delete=models.CASCADE)
    token_address = models.CharField(max_length=42, blank=True, null=True)

    def __str__(self):
        return f"{self.cryptocurrency.name} on {self.network.name} "


class Price(models.Model):
    cryptocurrency = models.ForeignKey("Cryptocurrency", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    snapshot = models.ForeignKey("Snapshot", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cryptocurrency.name} - {self.price} - {self.snapshot}"


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}"


class WalletType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    public_address = models.CharField(max_length=42)
    account = models.ForeignKey("Account", on_delete=models.CASCADE)
    wallet_type = models.ForeignKey(WalletType, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.public_address}"


class SnapshotAssets(models.Model):
    cryptocurrency = models.ForeignKey(
        "CryptocurrencyNetwork", on_delete=models.CASCADE
    )
    user_address = models.ForeignKey("UserAddress", on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    snapshot = models.ForeignKey("Snapshot", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cryptocurrency.cryptocurrency.name} - {self.quantity} - {self.snapshot}"


class Validator(models.Model):
    user_address = models.ForeignKey("UserAddress", on_delete=models.CASCADE)
    validator_index = models.IntegerField(unique=True)
    public_key = models.CharField(max_length=128)
    activation_date = models.CharField(max_length=20)

    def __str__(self):
        return f"Validator {self.validator_index} - {self.user_address}"


class ValidatorSnapshot(models.Model):
    validator = models.ForeignKey("Validator", on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=5)
    status = models.CharField(max_length=20)
    rewards = models.DecimalField(max_digits=20, decimal_places=5)
    snapshot = models.ForeignKey("Snapshot", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.validator} - {self.balance}"


class Protocol(models.Model):
    name = models.CharField(max_length=20)
    image = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}"


class ProtocolNetwork(models.Model):
    protocol = models.ForeignKey("Protocol", on_delete=models.CASCADE)
    network = models.ForeignKey("Network", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.protocol.name} on {self.network.name}"


class PoolType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name}"


class Pool(models.Model):
    type = models.ForeignKey("PoolType", on_delete=models.CASCADE)
    protocol_network = models.ForeignKey("ProtocolNetwork", on_delete=models.CASCADE)
    contract_address = models.CharField(max_length=42, null=True, blank=True)
    description = models.CharField(max_length=42, blank=True, null=True)

    def __str__(self):
        return f"{self.type} - {self.protocol_network}"


class PoolPosition(models.Model):
    pool = models.ForeignKey("Pool", on_delete=models.CASCADE)
    user_address = models.ForeignKey("UserAddress", on_delete=models.CASCADE)
    position_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.position_id}"


class PoolBalanceSnapshot(models.Model):
    pool_position = models.ForeignKey("PoolPosition", on_delete=models.CASCADE)
    token = models.ForeignKey("Cryptocurrency", on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    snapshot = models.ForeignKey("Snapshot", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pool_position} - {self.quantity} - {self.snapshot}"


class PoolRewardsSnapshot(models.Model):
    pool_position = models.ForeignKey("PoolPosition", on_delete=models.CASCADE)
    token = models.ForeignKey("Cryptocurrency", on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    snapshot = models.ForeignKey("Snapshot", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pool_position} - {self.quantity} - {self.snapshot}"


class Trove(models.Model):
    user_address = models.ForeignKey("UserAddress", on_delete=models.CASCADE)
    pool = models.ForeignKey("Pool", on_delete=models.CASCADE)
    trove_id = models.CharField(max_length=42)
    token = models.ForeignKey(
        "Cryptocurrency", on_delete=models.CASCADE
    )  # WETH, wstETH,rETH


class TroveSnapshot(models.Model):
    trove = models.ForeignKey("Trove", on_delete=models.CASCADE)
    collateral = models.DecimalField(max_digits=20, decimal_places=5)
    debt = models.DecimalField(max_digits=20, decimal_places=5)
    balance = models.DecimalField(max_digits=20, decimal_places=5)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    snapshot = models.ForeignKey("Snapshot", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.trove} - {self.collateral} - {self.snapshot}"


class Snapshot(models.Model):
    date = models.DateTimeField()

    class Meta:
        ordering = ["-date"]  # "Sort by descending date (most recent first)"

    def __str__(self):
        return f"{self.date}"
