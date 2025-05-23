from decimal import Decimal


import requests

from cryptotracker.models import CryptocurrencyPrice, Cryptocurrency


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


def fetch_historical_price(crypto_id, today, currency="eur"):
    """
    today = datetime.date.today().strftime("%d/%m/%y")

    today_d = datetime.strptime(fecha1_str, "%Y-%m-%d")

    last_d =
    """
    """
    days = 2


    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"

    params = {'vs_currency': currency, 'days': days, 'interval': 'daily'}


    data = APIquery(url, params)
    if data is None:
        return None

    print (data)

    prices = [price for price in data['prices']]

    print (prices)
    
    prices_dict = []

    for i in range(len(prices)):
        # Convert to seconds
        s = prices[i][0] / 1000
        prices_dict.append({'time' : datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d'),
                            'price' : prices[i][1]})
    """
    """
    days = today - prices_dict[1]['time']
    print(days)'
    """


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


def get_last_price(crypto_id: str, snapshot_date) -> Decimal:
    """
    Fetches the last price of a cryptocurrency from the database.
    Args:
        crypto_id (str): The ID of the cryptocurrency.
        snapshot_date (datetime): The date of the snapshot.
    Returns:
        Decimal: The last price of the cryptocurrency.
    """
    cryptocurrency = Cryptocurrency.objects.get(name=crypto_id)
    current_price = CryptocurrencyPrice.objects.filter(
        cryptocurrency=cryptocurrency, date__date=snapshot_date
    ).first()
    # if not current_price:
    #    current_price = fetch_historical_price(token.name, date= token_last_snapshot.snapshot_date.date())[-1]["price"]

    return current_price.price
