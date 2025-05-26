from decimal import Decimal
from datetime import datetime, timedelta

import requests

from cryptotracker.models import Price, Cryptocurrency


def APIquery(url, params) -> dict:
    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    if response.status_code != 200:
        print(
            f"{url} request {response.url} failed "
            f"with HTTP status code {response.status_code} and text "
            f"{response.text}",
        )
        return None
    return response.json()


def fetch_historical_price(crypto_id, date, currency="eur"):
    """
    Fetches historical price data for a cryptocurrency from the Coingecko API.
    Args:
        crypto_id (str): The ID of the cryptocurrency.
        date (datetime.date): The date for which to fetch the historical price.
        currency (str): The currency in which to fetch the price (default is "eur").
    Returns:
        list: A list of dictionaries containing the date and price.
    """
    
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/history"
    params = {'date': date.strftime('%d-%m-%Y')}

    data = APIquery(url, params)
    print( data)
    if data is None:
        return None
    print(data["market_data"]["current_price"][currency])
    return data["market_data"]["current_price"][currency]


def fetch_cryptocurrency_price(crypto_ids: list) -> list:
    """
    Fetches the current price of each cryptocurrency from the Coingecko API.
    Returns:
        list: A list of dictionaries containing the current price of each cryptocurrency.
    """

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(crypto_ids),
        "vs_currencies": "eur",
    }
    data = APIquery(url, params)
    return data


def convertWeiIntStr(value: int) -> str:
    ETH_THRESHOLD = 1 / Decimal(1e3)
    GWEI_THRESHOLD = 1 / Decimal(1e12)

    value = Decimal(value)

    if value < GWEI_THRESHOLD:
        return f"{value * Decimal(1e18).normalize():,.3f} wei"
    elif GWEI_THRESHOLD <= value < ETH_THRESHOLD:
        return f"{value * Decimal(1e9).normalize():,.3f} gwei"
    # value >= ETH_THRESHOLD
    return f"{value.normalize():,.3f} ether"


def get_last_price(crypto_id: str, snapshot) -> Decimal:
    """
    Fetches the last price of a cryptocurrency from the database or API if not found.
    Args:
        crypto_id (str): The ID of the cryptocurrency.
        snapshot (datetime): The date of the snapshot.
    Returns:
        Decimal: The last price of the cryptocurrency.
    """
    cryptocurrency = Cryptocurrency.objects.get(name=crypto_id)
    current_price = Price.objects.filter(
        cryptocurrency=cryptocurrency, snapshot__date=snapshot
    ).first()

    if not current_price:
        # Fetch historical price if not found in the database
        historical_price = fetch_historical_price(crypto_id, snapshot)
        if historical_price:
            # Assuming the last price in the list corresponds to the snapshot date
            return Decimal( historical_price)
        else:
            raise ValueError(f"Price data for {crypto_id} on {snapshot.date} not found.")

    return current_price.price