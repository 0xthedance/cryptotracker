from datetime import datetime
from ape import Contract, networks

from cryptotracker.utils import get_last_price
from cryptotracker.models import (
    Address,
    SnapshotAssets,
    CryptocurrencyNetwork,
    Network,
)


def fetch_assets(address: Address, snapshot_date) -> None:
    """
    Fetches the assets of a user from the Ethereum blockchain and stores them in the database.
    This function uses the Ape library to interact with the Ethereum blockchain and fetch the balance of each token.
    It also fetches the current price of each token using the fetch_historical_price function from Coingeko app

    """
    crypto_networks = Network.objects.all()
    for network in crypto_networks:
        with networks.parse_network_choice(network.url_rpc) as provider:
            public_address = address.public_address
            # Fetch tokens balance
            for token in CryptocurrencyNetwork.objects.filter(network=network):
                print(token)
                if token.cryptocurrency.name == "ethereum":
                    token_asset = provider.get_balance(public_address)
                else:
                    token_contract = Contract(token.address)
                    token_asset = token_contract.balanceOf(public_address)

                if token_asset != 0:

                    asset_snapshot = SnapshotAssets(
                        cryptocurrency=token,
                        address=address,
                        quantity=token_asset / 1e18,
                        snapshot_date=snapshot_date.date,
                    )
                    asset_snapshot.save()


def fetch_aggregated_assets(addresses: list) -> dict:
    """
    Fetches the aggregated assets of a list of accounts.
    Args:
        accounts (list): A list of account objects.
    Returns:
        dict: A dictionary containing the aggregated assets and their values.
    """

    aggregated_assets = {}

    for address in addresses:
        assets_list = SnapshotAssets.objects.filter(address=address)
        if not assets_list:
            continue

        for network in Network.objects.all():
            tokens = CryptocurrencyNetwork.objects.filter(network=network)
            network_assets = assets_list.filter(cryptocurrency__network=network)
            if not network_assets:
                continue

            for token in tokens:
                token_last_snapshot = (
                    network_assets.filter(cryptocurrency=token)
                    .order_by("-snapshot_date")
                    .first()
                )

                if not token_last_snapshot:
                    continue

                current_price = get_last_price(
                    token.cryptocurrency.name, token_last_snapshot.snapshot_date.date()
                )

                asset = token_last_snapshot

                if asset.cryptocurrency.cryptocurrency.symbol in aggregated_assets:
                    aggregated_assets[asset.cryptocurrency.cryptocurrency.symbol][
                        "amount"
                    ] += asset.quantity

                else:
                    aggregated_assets[asset.cryptocurrency.cryptocurrency.symbol] = {
                        "network": network.name,
                        "amount": asset.quantity,
                        "image": asset.cryptocurrency.cryptocurrency.image,
                        "last_snapshot_date": asset.snapshot_date,
                    }
                aggregated_assets[asset.cryptocurrency.cryptocurrency.symbol][
                    "amount_eur"
                ] = (
                    aggregated_assets[asset.cryptocurrency.cryptocurrency.symbol][
                        "amount"
                    ]
                    * current_price
                )
    return aggregated_assets
