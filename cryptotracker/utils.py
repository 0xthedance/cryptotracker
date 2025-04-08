import datetime
from decimal import Decimal

import requests


def APIquery(url, params) -> dict:
    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    if response.status_code != 200:
        print(
            f"Beaconchain node request {response.url} failed "
            f"with HTTP status code {response.status_code} and text "
            f"{response.text}",
        )
        return None
    return response.json()


def fetch_historical_price(crypto_id, currency="eur"):
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
    prices_dict = [{"time": "today", "price": 1}]

    return prices_dict


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


# print(fetch_assets('0xb26E1cD0AfC11aAc6a9D27F531Aa3F2559Cf289f'))
