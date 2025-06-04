from celery import shared_task
from datetime import datetime
from celery.exceptions import TimeoutError

from cryptotracker.tokens import fetch_assets
from cryptotracker.models import Address, Snapshot, Cryptocurrency, Price
from cryptotracker.staking import fetch_staking_assets
from cryptotracker.utils import fetch_cryptocurrency_price
from cryptotracker.protocols.liquity import update_lqty_pools
from cryptotracker.protocols.aave import update_aave_lending_pools
from cryptotracker.protocols.uniswap import update_uniswap_v3_positions


@shared_task
def create_snapshot() -> int:
    """
    Creates a new Snapshot entry and returns its ID.
    Returns:
        int: The ID of the created Snapshot.
    """
    snapshot = Snapshot.objects.create(date=datetime.now())
    return snapshot.id


@shared_task
def update_cryptocurrency_price(snapshot_id: int) -> str:
    """
    Fetches the current price of each cryptocurrency and stores it in the database with the given Snapshot.
    Args:
        snapshot_id (int): The ID of the Snapshot to associate with the prices.
    Returns:
        str: A success message.
    """
    print(snapshot_id)
    snapshot = Snapshot.objects.get(id=snapshot_id)
    cryptocurrencies = Cryptocurrency.objects.all()
    crypto_ids = [crypto.name for crypto in cryptocurrencies]

    prices = fetch_cryptocurrency_price(crypto_ids)
    if prices is None:
        print("Failed to fetch cryptocurrency prices.")
        return "Failed to update cryptocurrency prices."
    
    for crypto in crypto_ids:
        crypto_price = Price(
            cryptocurrency=Cryptocurrency.objects.get(name=crypto),
            price=prices[crypto]["eur"],
            snapshot=snapshot,
        )
        crypto_price.save()
        print(f"Price of {crypto} updated to {prices[crypto]['eur']} EUR")
    return "Cryptocurrency prices updated successfully!"


@shared_task
def update_assets_database(snapshot_id: int) -> str:
    """
    Fetches the assets of a user and stores them in the database with the given Snapshot.
    Args:
        snapshot_id (int): The ID of the Snapshot to associate with the assets.
    Returns:
        str: A success message.
    """
    print("Updating assets database...")
    snapshot = Snapshot.objects.get(id=snapshot_id)

    addresses = Address.objects.all()
    for address in addresses:
        try:
            print(f"Fetching assets for address: {address.public_address}")
            fetch_assets(address, snapshot)
        except TimeoutError:
            print("TimeoutError: Retrying...")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    return "Assets updated successfully!"


@shared_task
def update_staking_assets(snapshot_id: int) -> str:
    """
    Fetches the staking assets of a user and stores them in the database with the given Snapshot.
    Args:
        snapshot_id (int): The ID of the Snapshot to associate with the staking assets.
    Returns:
        str: A success message.
    """
    snapshot = Snapshot.objects.get(id=snapshot_id)

    addresses = Address.objects.all()
    for address in addresses:
        try:
            fetch_staking_assets(address, snapshot)
        except TimeoutError:
            print("TimeoutError: Retrying...")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    return "Staking assets updated successfully!"


@shared_task
def update_protocols(snapshot_id: int) -> str:
    """
    Fetches the protocols of a user and stores them in the database with the given Snapshot.
    Args:
        snapshot_id (int): The ID of the Snapshot to associate with the protocols.
    Returns:
        str: A success message.
    """
    snapshot = Snapshot.objects.get(id=snapshot_id)

    addresses = Address.objects.all()
    for address in addresses:
        try:
            print(f"Fetching protocols for address: {address}")
            update_lqty_pools(address, snapshot)
            update_aave_lending_pools(address, snapshot)
            update_uniswap_v3_positions(address, snapshot)
        except TimeoutError:
            print("TimeoutError: Retrying...")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    return "Protocols updated successfully!"
