from celery import shared_task
from datetime import datetime
from celery.exceptions import TimeoutError
from cryptotracker.tokens import fetch_assets
from cryptotracker.models import (
    Address,
    SnapshotDate,
    Cryptocurrency,
    CryptocurrencyPrice,
)
from cryptotracker.staking import fetch_staking_assets
from cryptotracker.utils import fetch_cryptocurrency_price
from cryptotracker.protocols.liquity import update_lqty_pools
from cryptotracker.protocols.aave import update_aave_lending_pools


@shared_task
def create_snapshot_date():
    """
    Creates a new SnapshotDate entry and returns its ID.
    """
    snapshot_date = SnapshotDate.objects.create(date=datetime.now())
    return snapshot_date.id


@shared_task
def update_cryptocurrency_price(snapshot_date_id):
    """
    Fetches the current price of each cryptocurrency and stores it in the database with the given SnapshotDate.
    """
    snapshot_date = SnapshotDate.objects.get(id=snapshot_date_id)
    cryptocurrencies = Cryptocurrency.objects.all()
    crypto_ids = [crypto.name for crypto in cryptocurrencies]

    prices = fetch_cryptocurrency_price(crypto_ids)
    for crypto in crypto_ids:
        crypto_price = CryptocurrencyPrice(
            cryptocurrency=Cryptocurrency.objects.get(name=crypto),
            price=prices[crypto]["eur"],
            date=snapshot_date.date,
        )
        crypto_price.save()
        print(f"Price of {crypto} updated to {prices[crypto]['eur']} EUR")
    return "Cryptocurrency prices updated successfully!"


@shared_task
def update_assets_database(snapshot_date_id):
    """
    Fetches the assets of a user and stores them in the database with the given SnapshotDate.
    """
    snapshot_date = SnapshotDate.objects.get(id=snapshot_date_id)
    print("Updating assets database...")
    addresses = Address.objects.all()
    for address in addresses:
        try:
            print(f"Fetching assets for address: {address.public_address}")
            fetch_assets(address, snapshot_date)
        except TimeoutError:
            print("TimeoutError: Retrying...")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    return "Assets updated successfully!"


@shared_task
def update_staking_assets(snapshot_date_id):
    """
    Fetches the staking assets of a user and stores them in the database with the given SnapshotDate.
    """
    snapshot_date = SnapshotDate.objects.get(id=snapshot_date_id)
    addresses = Address.objects.all()
    for address in addresses:
        try:
            fetch_staking_assets(address, snapshot_date)
        except TimeoutError:
            print("TimeoutError: Retrying...")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    return "Staking assets updated successfully!"


@shared_task
def update_protocols(snapshot_date_id):
    """
    Fetches the protocols of a user and stores them in the database with the given SnapshotDate.
    """
    snapshot_date = SnapshotDate.objects.get(id=snapshot_date_id)
    addresses = Address.objects.all()
    for address in addresses:
        try:
            print(f"Fetching protocols for address: {address.public_address}")
            update_lqty_pools(address.public_address, snapshot_date)
            update_aave_lending_pools(address.public_address, snapshot_date)
        except TimeoutError:
            print("TimeoutError: Retrying...")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    return "Protocols updated successfully!"
