from ape import Contract, networks

from cryptotracker.utils import fetch_historical_price

TOKENS = [
    {
        "name": "ethereum",
        "symbol": "ETH",
        "image": "cryptotracker/logos/ethereum.png",
        "address": "0x",
    },
    {
        "name": "liquity",
        "symbol": "LQTY",
        "image": "cryptotracker/logos/liquity.png",
        "address": "0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D",
    },
    {
        "name": "ssv-network",
        "symbol": "SSV",
        "image": "cryptotracker/logos/ssv.png",
        "address": "0x9D65fF81a3c488d585bBfb0Bfe3c7707c7917f54",
    },
    {
        "name": "balancer",
        "symbol": "BAL",
        "image": "cryptotracker/logos/bal.png",
        "address": "0xba100000625a3754423978a60c9317c58a424e3d",
    },
    {
        "name": "liquity-usd",
        "symbol": "LUSD",
        "image": "cryptotracker/logos/lusd.png",
        "address": "0x5f98805a4e8be255a32880fdec7f6728c6568ba0",
    },
    {
        "name": "safe",
        "symbol": "SAFE",
        "image": "cryptotracker/logos/safe.png",
        "address": "0x5afe3855358e112b5647b952709e6165e1c1eeee",
    },
]


def fetch_assets(user_address: str) -> list[dict]:
    """
    Fetches the assets of a user from the Ethereum blockchain.
    Args:
        user_address (str): The address of the user.
    Returns:
        list[dict]: A list of dictionaries containing the assets and their values.
    """

    assets_dict = []
    print(type(user_address))

    with networks.parse_network_choice("ethereum:mainnet:alchemy") as provider:

        # Fetch tokens balance
        for token in TOKENS:
            if token["name"] == "ethereum":
                token_asset = provider.get_balance(user_address)
            else:
                token_contract = Contract(token["address"])
                token_asset = token_contract.balanceOf(user_address)

            if token_asset != 0:
                current_price = fetch_historical_price(token["name"])[-1]["price"]
                assets_dict.append(
                    {
                        "cryptocurrency": token["symbol"],
                        "amount": token_asset / 1e18,  # Convert to token
                        "amount_eur": (token_asset / 1e18) * current_price,
                        "image": token["image"],
                    }
                )
        return assets_dict


def fetch_aggregated_assets(accounts: list) -> dict:
    """
    Fetches the aggregated assets of a list of accounts.
    Args:
        accounts (list): A list of account objects.
    Returns:
        dict: A dictionary containing the aggregated assets and their values.
    """

    aggregated_assets = {}

    for account in accounts:
        assets_dict = fetch_assets(account.public_address)

        for asset in assets_dict:
            if asset["cryptocurrency"] in aggregated_assets:
                aggregated_assets[asset["cryptocurrency"]]["amount"] += asset["amount"]
                aggregated_assets[asset["cryptocurrency"]]["amount_eur"] += asset[
                    "amount_eur"
                ]
            else:
                aggregated_assets[asset["cryptocurrency"]] = {
                    "amount": asset["amount"],
                    "amount_eur": asset["amount_eur"],
                    "image": asset["image"],
                }
    for key, value in aggregated_assets.items():
        value["amount"] = f"{value['amount']:,.2f}".ljust(16) + key
        euro = "€"
        value["amount_eur"] = f'{value["amount_eur"]:,.2f}'.ljust(16) + euro
    return aggregated_assets
