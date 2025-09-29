import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

import backoff
import requests


from cryptotracker.models import Cryptocurrency, Price


def log_backoff(details):
    logging.warning(
        f"Backing off {details['wait']:0.1f} seconds after {details['tries']} tries."
    )


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.RequestException, ValueError, KeyError),
    max_tries=3,
    max_time=180,
    on_backoff=log_backoff,
)
def APIquery(url: str, params: Dict) -> Optional[Dict]:
    """
    Sends a GET request to the specified URL with the given parameters.
    Args:
        url (str): The URL to query.
        params (dict): The query parameters.
    Returns:
        dict: The JSON response from the API, or None if the request fails.
    """
    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as e:
        logging.error(f"{url} request failed: {e}")
        return None

    if response.status_code != 200:
        logging.error(
            f"{url} request {response.url} failed "
            f"with HTTP status code {response.status_code} and text "
            f"{response.text}",
        )
        return None
    return response.json()


def fetch_historical_price(
    crypto_id: str, date: date, currency: str = "eur"
) -> Optional[Decimal]:
    """
    Fetches historical price data for a cryptocurrency from the Coingecko API.
    Args:
        crypto_id (str): The ID of the cryptocurrency.
        date (datetime.date): The date for which to fetch the historical price.
        currency (str): The currency in which to fetch the price (default is "eur").
    Returns:
        Decimal: The historical price of the cryptocurrency, or None if the request fails.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/history"
    params = {"date": date.strftime("%d-%m-%Y")}

    data = APIquery(url, params)
    if data is None:
        return None
    return Decimal(data["market_data"]["current_price"][currency])


def fetch_cryptocurrency_price(
    crypto_ids: List[str],
) -> Optional[Dict[str, Dict[str, Decimal]]]:
    """
    Fetches the current price of each cryptocurrency from the Coingecko API.
    Args:
        crypto_ids (list): A list of cryptocurrency IDs.
    Returns:
        dict: A dictionary containing the current price of each cryptocurrency, or None if the request fails.
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(crypto_ids),
        "vs_currencies": "eur",
    }
    data = APIquery(url, params)
    return data


def convertWeiIntStr(value: int) -> str:
    """
    Converts a value in Wei to a human-readable string format (Wei, Gwei, or Ether).
    Args:
        value (int): The value in Wei.
    Returns:
        str: The human-readable string representation of the value.
    """
    ETH_THRESHOLD = 1 / Decimal(1e3)
    GWEI_THRESHOLD = 1 / Decimal(1e12)

    value_decimal = Decimal(value)

    if value_decimal < GWEI_THRESHOLD:
        return f"{value_decimal * Decimal(1e18).normalize():,.3f} wei"
    elif GWEI_THRESHOLD <= value_decimal < ETH_THRESHOLD:
        return f"{value_decimal * Decimal(1e9).normalize():,.3f} gwei"
    # value >= ETH_THRESHOLD
    return f"{value_decimal.normalize():,.3f} ether"


def get_last_price(crypto_id: str, snapshot: datetime) -> Decimal:
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
        historical_price = fetch_historical_price(crypto_id, snapshot.date())
        if historical_price:
            return historical_price
        else:
            raise ValueError(
                f"Price data for {crypto_id} on {snapshot.date()} not found."
            )

    return current_price.price
