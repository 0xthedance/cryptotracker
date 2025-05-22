from cryptotracker.models import (
    Network,
    Pool,
    Protocol,
    PoolBalance,
    PoolRewards,
    Address,
    SnapshotTrove
)

from cryptotracker.utils import get_last_price
from datetime import datetime

from django.db.models import Max


def save_pool_balance(address, pool, token, quantity, date):
    """
    Saves the pool balance to the database.
    Args:
        pool (Pool): The pool object.
        token (Cryptocurrency): The cryptocurrency object.
        quantity (float): The quantity of the token.
    """
    try:
        pool_balance = PoolBalance(
            address=Address.objects.get(public_address=address),
            pool=pool,
            token=token,
            quantity=quantity,
            snapshot_date=date.date,
        )
        print(pool_balance)

        pool_balance.save()
    except Exception as e:
        print(f"Error saving pool {pool.name} balance: {e}")


def save_pool_rewards(address, pool, token, quantity, date):
    """
    Saves the pool rewards to the database.
    Args:
        pool (Pool): The pool object.
        token (Cryptocurrency): The cryptocurrency object.
        quantity (float): The quantity of the token.
    """
    pool_rewards = PoolRewards(
        address=Address.objects.get(public_address=address),
        pool=pool,
        token=token,
        quantity=quantity,
        snapshot_date=date.date,
    )
    print (pool_rewards)
    pool_rewards.save()


def get_protocols_snapshots(addresses: list, protocol_name: str) -> dict:
    """
    Fetches the last snapshot of the protocols in the database.
    This function iterates through all the protocols and their pools, fetching the data from the database
    and returning it as a dictionary.
    """
    last_pool_data = {}
    protocols = Protocol.objects.filter(name=protocol_name)
    for protocol in protocols:
        pools_balances = PoolBalance.objects.filter(
            address__in=addresses, pool__protocol=protocol
        )
        pools_rewards = PoolRewards.objects.filter(
            address__in=addresses, pool__protocol=protocol
        )
        if not pools_balances:
            continue

        pools = Pool.objects.filter(protocol=protocol)
        for pool in pools:
            last_pool_data[pool.name] = {
                "balances": {},
                "rewards": {},
                "troves":[],
            }

            if pool.name == "borrow":
                troves = SnapshotTrove.objects.filter(address__in=addresses, pool=pool)
                if not troves:
                    continue
                latest_troves = troves.values("trove_id").annotate(latest_trove_data=Max("snapshot_date"))
                last_troves = troves.filter(snapshot_date__in=[entry["latest_trove_data"] for entry in latest_troves])
                last_pool_data[pool.name]["troves"].append(last_troves)
                continue


            pool_balances = pools_balances.filter(pool=pool)
            pool_rewards = pools_rewards.filter(pool=pool)
            if not pool_balances:
                continue

            latest_balances = pool_balances.values(
                "token__name"
            ).annotate(  # Group by token__name
                latest_balance_date=Max("snapshot_date")
            )  # Get the latest snapshot_date for each group
            latest_rewards = pool_rewards.values(
                "token__name"
            ).annotate(  # Group by token__name
                latest_rewards_date=Max("snapshot_date")
            )  # Get the latest snapshot_date for each group

            last_balances = pool_balances.filter(
                snapshot_date__in=[
                    entry["latest_balance_date"] for entry in latest_balances
                ]
            )
            last_rewards = pool_rewards.filter(
                snapshot_date__in=[
                    entry["latest_rewards_date"] for entry in latest_rewards
                ]
            )

            for balance in last_balances:
                current_price = get_last_price(
                    balance.token.name, balance.snapshot_date.date()
                )
                last_pool_data[pool.name]["balances"][balance.token.symbol] = {
                    "network": balance.pool.protocol.network.name,
                    "quantity": balance.quantity,
                    "balance_eur": balance.quantity * current_price,
                    "image": balance.token.image,
                }
            for reward in last_rewards:
                last_pool_data[pool.name]["rewards"][reward.token.symbol] = {
                    "quantity": reward.quantity,
                }

    return last_pool_data