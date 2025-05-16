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
def update_cryptocurrency_price():
    """
    Fetches the current price of each cryptocurrency every 24h from the Coingecko API and stores it in the database.
    This function uses the Coingecko API to fetch the current price of each cryptocurrency and stores it in the database.
    """
    cryptocurrencies = Cryptocurrency.objects.all()
    crypto_ids = [crypto.name for crypto in cryptocurrencies]

    prices = fetch_cryptocurrency_price(crypto_ids)
    for crypto in crypto_ids:
        crypto_price = CryptocurrencyPrice(
            cryptocurrency=Cryptocurrency.objects.get(name=crypto),
            price=prices[crypto]["eur"],
            date=datetime.now(),
        )
        crypto_price.save()
        print(f"Price of {crypto} updated to {prices[crypto]['eur']} EUR")
    return "Cryptocurrency prices updated successfully!"


@shared_task
def update_assets_database():
    """
    Fetches the assets of a user every 24h from the Ethereum blockchain and stores them in the database.
    This function uses the Ape library to interact with the Ethereum blockchain and fetch the balance of each token.
    It also fetches the current price of each token using the fetch_historical_price function from Coingeko app
    """
    print("Updating assets database...")
    addresses = Address.objects.all()
    for address in addresses:
        try:
            print(f"Fetching assets for address: {address.public_address}")
            fetch_assets(address)
        except TimeoutError:
            print("TimeoutError: Retrying...")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
        SnapshotDate.objects.create(
            date=datetime.now(),
            address=address,
        )
    return "Assets updated successfully!"


@shared_task
def update_staking_assets():
    """
    Fetches the staking assets of a user every 24h from the Ethereum blockchain and stores them in the database.
    This function uses the Ape library to interact with the Ethereum blockchain and fetch the balance of each token.
    It also fetches the current price of each token using the fetch_historical_price function from Coingeko app
    """

    addresses = Address.objects.all()
    for address in addresses:
        try:
            fetch_staking_assets(address)
        except TimeoutError:
            print("TimeoutError: Retrying...")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    return "Staking assets updated successfully!"

@shared_task
def update_protocols():
    """
    Fetches the protocols of a user every 24h from the Ethereum blockchain and stores them in the database.
    This function uses the Ape library to interact with the Ethereum blockchain and fetch the balance of each token.
    It also fetches the current price of each token using the fetch_historical_price function from Coingeko app
    """

    addresses = Address.objects.all()
    for address in addresses:
        try:
            print(f"Fetching protocols for address: {address.public_address}")
            update_lqty_pools(address.public_address)
            update_aave_lending_pools(address.public_address)
        except TimeoutError:
            print("TimeoutError: Retrying...")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    return "Protocols updated successfully!"
