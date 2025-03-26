
from ape import Contract, networks,convert
from decimal import Decimal
import requests
import datetime



CRIPTOCURRENCIES = ["ethereum", "liquity"]
LQTY_CONTRACT = '0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D'

def fetch_assets(user_address):

    assets_dict = []
    print(type(user_address))

    with networks.parse_network_choice("ethereum:mainnet:alchemy") as provider:


        # Fetch ETH balance
        eth_asset = provider.get_balance(user_address)
        if eth_asset != 0:
            current_price = fetch_historical_data("ethereum")[-1]["price"]
            assets_dict.append({
                'cryptocurrency': 'ETH',
                'amount': eth_asset / 1e18,  # Convert to ETH
                'amount_eur': (eth_asset / 1e18) * current_price,
            })

        # Fetch LQTY balance
        contract = Contract(LQTY_CONTRACT)
        lqty_asset = contract.balanceOf(user_address)
        if lqty_asset != 0:
            current_price = fetch_historical_data("liquity")[-1]["price"]
            assets_dict.append({
                'cryptocurrency': 'LQTY',
                'amount': lqty_asset / 1e18,  # Convert to LQTY
                'amount_eur': (lqty_asset / 1e18) * current_price,
            })

        print(assets_dict)
        return assets_dict

def fetch_aggregated_assets(accounts):
    aggregated_assets = {}

    for account in accounts:
        assets_dict = fetch_assets(account.public_address)

        for asset in assets_dict:
            if asset['cryptocurrency'] in aggregated_assets:
                aggregated_assets[asset['cryptocurrency']]['amount'] += asset['amount']
                aggregated_assets[asset['cryptocurrency']]['amount_eur'] += asset['amount_eur']
            else:
                aggregated_assets[asset['cryptocurrency']] = {
                    'amount': asset['amount'],
                    'amount_eur': asset['amount_eur']
                }
    print(aggregated_assets)
    return aggregated_assets


def fetch_historical_data(crypto_id, currency='eur'):
    '''
    today = datetime.date.today().strftime("%d/%m/%y")

    today_d = datetime.strptime(fecha1_str, "%Y-%m-%d")

    last_d =
    '''
    days = 2


    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"

    params = {'vs_currency': currency, 'days': days, 'interval': 'daily'}

    response = requests.get(url, params=params)

    data = response.json()

    print (data)

    prices = [price for price in data['prices']]

    print (prices)
    
    prices_dict = []

    for i in range(len(prices)):
        # Convert to seconds
        s = prices[i][0] / 1000
        prices_dict.append({'time' : datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d'),
                            'price' : prices[i][1]})
    '''
    days = today - prices_dict[1]['time']
    print(days)'
    '''

    return prices_dict


#print(fetch_assets('0xb26E1cD0AfC11aAc6a9D27F531Aa3F2559Cf289f'))
