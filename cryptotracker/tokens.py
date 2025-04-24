from datetime import datetime
from ape import Contract, networks

from cryptotracker.utils import get_last_price
from cryptotracker.models import (
    Account,
    SnapshotAssets,
    Cryptocurrency,
    CryptocurrencyPrice,
)

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


def fetch_assets(account: Account) -> None:
    """
    Fetches the assets of a user from the Ethereum blockchain and stores them in the database.
    This function uses the Ape library to interact with the Ethereum blockchain and fetch the balance of each token.
    It also fetches the current price of each token using the fetch_historical_price function from Coingeko app

    """
    with networks.parse_network_choice("ethereum:mainnet:alchemy") as provider:
        public_address = account.public_address
        # Fetch tokens balance
        for token in Cryptocurrency.objects.all():
            if token.name == "ethereum":
                token_asset = provider.get_balance(public_address)
            else:
                token_contract = Contract(token.address)
                token_asset = token_contract.balanceOf(public_address)

            if token_asset != 0:

                asset_snapshot = SnapshotAssets(
                    cryptocurrency=token,
                    account=account,
                    quantity=token_asset / 1e18,
                    snapshot_date=datetime.now(),
                )
                asset_snapshot.save()


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
        assets_list = SnapshotAssets.objects.filter(account=account)
        if not assets_list:
            continue

        for token in Cryptocurrency.objects.all():
            token_last_snapshot = (
                assets_list.filter(cryptocurrency=token)
                .order_by("-snapshot_date")
                .first()
            )

            if not token_last_snapshot:
                continue

            current_price = get_last_price(
                token.name, token_last_snapshot.snapshot_date.date()
            )

            asset = token_last_snapshot

            if asset.cryptocurrency.symbol in aggregated_assets:
                aggregated_assets[asset.cryptocurrency.symbol][
                    "amount"
                ] += asset.quantity

            else:
                aggregated_assets[asset.cryptocurrency.symbol] = {
                    "amount": asset.quantity,
                    "image": asset.cryptocurrency.image,
                    "last_snapshot_date": asset.snapshot_date,
                }
            aggregated_assets[asset.cryptocurrency.symbol]["amount_eur"] = (
                aggregated_assets[asset.cryptocurrency.symbol]["amount"] * current_price
            )
    return aggregated_assets
