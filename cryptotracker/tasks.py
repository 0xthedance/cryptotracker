import logging

from datetime import datetime
from typing import Optional

from celery import shared_task, group
from celery.exceptions import TimeoutError

from cryptotracker.models import Cryptocurrency, Price, Snapshot, UserAddress
from cryptotracker.protocols.aave import update_aave_lending_pools
from cryptotracker.protocols.liquity_pools import update_lqty_pools
from cryptotracker.protocols.uniswap import update_uniswap_v3_positions
from cryptotracker.eth_staking import fetch_staking_assets
from cryptotracker.tokens import fetch_assets
from cryptotracker.utils import fetch_cryptocurrency_price


@shared_task(bind=True)
def run_daily_snapshot_update(self, user_id: Optional[int] = None) -> group:
    """
    Coordinates the daily snapshot update process.
    Creates a snapshot and then runs all update tasks in parallel.
    """
    # Create the snapshot first
    snapshot_id = create_snapshot()

    # Run tasks in parallel
    task_group = group(
        update_cryptocurrency_price.s(snapshot_id),
        update_assets_database.s(snapshot_id, user_id),
        update_staking_assets.s(snapshot_id, user_id),
        update_protocols.s(snapshot_id, user_id),
    )

    result = task_group.apply_async()
    return result


@shared_task(bind=True)
def create_snapshot(self) -> int:
    """
    Creates a new Snapshot entry and returns its ID.
    Returns:
        int: The ID of the created Snapshot.
    """
    snapshot = Snapshot.objects.create(date=datetime.now())
    return snapshot.id


@shared_task(bind=True)
def update_cryptocurrency_price(self, snapshot_id: int) -> str:
    """
    Fetches the current price of each cryptocurrency and stores it in the database with the given Snapshot.
    Args:
        snapshot_id (int): The ID of the Snapshot to associate with the prices.
    Returns:
        str: A success message.
    """
    logging.info("Updating cryptocurrency prices...", snapshot_id)
    snapshot = Snapshot.objects.get(id=snapshot_id)
    cryptocurrencies = Cryptocurrency.objects.all()
    crypto_ids = [crypto.name for crypto in cryptocurrencies]

    prices = fetch_cryptocurrency_price(crypto_ids)
    if prices is None:
        logging.error("Failed to fetch cryptocurrency prices.")
        return "Failed to update cryptocurrency prices."

    for crypto in crypto_ids:
        crypto_price = Price(
            cryptocurrency=Cryptocurrency.objects.get(name=crypto),
            price=prices[crypto]["eur"],
            snapshot=snapshot,
        )
        crypto_price.save()
        logging.info(f"Price of {crypto} updated to {prices[crypto]['eur']} EUR")
    return "Cryptocurrency prices updated successfully!"


@shared_task(bind=True)
def update_assets_database(self, snapshot_id: int, user_id: Optional[int]) -> str:
    """
    Fetches the assets of a user and stores them in the database with the given Snapshot.
    Args:
        snapshot_id (int): The ID of the Snapshot to associate with the assets.
    Returns:
        str: A success message.
    """
    logging.info("Updating assets database...")
    snapshot = Snapshot.objects.get(id=snapshot_id)

    if user_id is None:
        logging.info("Automated daily snapshot update initiated.")
        user_addresses = UserAddress.objects.all()
    else:
        logging.info(f"User initiated a daily snapshot update with user ID: {user_id}")
        user_addresses = UserAddress.objects.filter(user_id=user_id)

    for user_address in user_addresses:
        try:
            logging.info(
                f"Fetching assets for user_address: {user_address.public_address}"
            )
            fetch_assets(user_address, snapshot)
        except TimeoutError:
            logging.error("TimeoutError: Retrying...")
            continue
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            continue
    return "Assets updated successfully!"


@shared_task(bind=True)
def update_staking_assets(self, snapshot_id: int, user_id: Optional[int]) -> str:
    """
    Fetches the staking assets of a user and stores them in the database with the given Snapshot.
    Args:
        snapshot_id (int): The ID of the Snapshot to associate with the staking assets.
    Returns:
        str: A success message.
    """
    snapshot = Snapshot.objects.get(id=snapshot_id)

    if user_id is None:
        logging.info("Automated daily snapshot update initiated.")
        user_addresses = UserAddress.objects.all()
    else:
        logging.info(f"User initiated a daily snapshot update with user ID: {user_id}")
        user_addresses = UserAddress.objects.filter(user_id=user_id)

    for user_address in user_addresses:
        try:
            logging.info(
                f"Fetching staking assets for user_address: {user_address.public_address}"
            )
            fetch_staking_assets(user_address, snapshot)
        except TimeoutError:
            logging.error("TimeoutError: Retrying...")
            continue
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            continue
    return "Staking assets updated successfully!"


@shared_task(bind=True)
def update_protocols(self, snapshot_id: int, user_id: Optional[int]) -> str:
    """
    Fetches the protocols of a user and stores them in the database with the given Snapshot.
    Args:
        snapshot_id (int): The ID of the Snapshot to associate with the protocols.
    Returns:
        str: A success message.
    """

    snapshot = Snapshot.objects.get(id=snapshot_id)

    if user_id is None:
        logging.info("Automated daily snapshot update initiated.")
        user_addresses = UserAddress.objects.all()
    else:
        logging.info(f"User initiated a daily snapshot update with user ID: {user_id}")
        user_addresses = UserAddress.objects.filter(user_id=user_id)

    for user_address in user_addresses:
        try:
            logging.info(f"Fetching protocols for user_address: {user_address}")
            update_lqty_pools(user_address, snapshot)
            update_aave_lending_pools(user_address, snapshot)
            update_uniswap_v3_positions(user_address, snapshot)
        except TimeoutError:
            logging.error("TimeoutError: Retrying...")
            continue
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            continue
    return "Protocols updated successfully!"
