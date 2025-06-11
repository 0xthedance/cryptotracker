from decimal import Decimal
from ape import Contract, networks

from cryptotracker.utils import get_last_price
from cryptotracker.models import (
    UserAddress,
    SnapshotAssets,
    CryptocurrencyNetwork,
    Network,
    Snapshot,
)


def fetch_assets(user_address: UserAddress, snapshot: Snapshot) -> None:
    """
    Fetches the assets of a user from the Ethereum blockchain and stores them in the database.
    This function uses the Ape library to interact with the Ethereum blockchain and fetch the balance of each token.
    It also fetches the current price of each token using the fetch_historical_price function from Coingeko app

    """
    crypto_networks = Network.objects.all()
    for network in crypto_networks:
        with networks.parse_network_choice(network.url_rpc) as provider:
            public_address = user_address.public_address
            # Fetch tokens balance
            for token in CryptocurrencyNetwork.objects.filter(network=network):
                print(token)
                if token.cryptocurrency.name == "ethereum":
                    token_asset = provider.get_balance(public_address)
                else:
                    token_contract = Contract(token.token_address)
                    token_asset = token_contract.balanceOf(public_address)

                if token_asset != 0:

                    asset_snapshot = SnapshotAssets(
                        cryptocurrency=token,
                        user_address=user_address,
                        quantity=token_asset / 1e18,
                        snapshot=snapshot,
                    )
                    asset_snapshot.save()


def fetch_aggregated_assets(user_addresses: list[UserAddress]) -> dict:
    """
    Fetches the aggregated assets of a list of user_addresses.
    Args:
        user_addresses (list): A list of UserAddress objects.
    Returns:
        dict: A dictionary containing the aggregated assets and their values.
    """
    last_snapshot = Snapshot.objects.first()
    if not last_snapshot:
        return {}

    # Filter assets for the given user_addresses and snapshot date
    last_assets = SnapshotAssets.objects.filter(
        user_address__in=user_addresses, snapshot=last_snapshot
    )

    if not last_assets.exists():
        return {}

    # Aggregate assets by cryptocurrency and network
    aggregated_assets: dict = {}
    for asset in last_assets:
        token = asset.cryptocurrency.cryptocurrency
        network = asset.cryptocurrency.network
        symbol = token.symbol

        # Use a combination of symbol and network name as the key
        key = f"{symbol}_{network.name}"

        # Fetch the current price
        current_price = get_last_price(token.name, last_snapshot.date)

        # Update or initialize the aggregated data
        if key not in aggregated_assets:
            aggregated_assets[key] = {
                "symbol": symbol,
                "network": network.name,
                "amount": Decimal(0),
                "image": token.image,
                "amount_eur": Decimal(0),
            }

        aggregated_assets[key]["amount"] += asset.quantity
        aggregated_assets[key]["amount_eur"] = (
            aggregated_assets[key]["amount"] * current_price
        )

    return aggregated_assets
