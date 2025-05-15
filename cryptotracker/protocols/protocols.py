from cryptotracker.models import Network, Pool, Protocol, PoolBalance, Cryptocurrency, PoolRewards, Address

from cryptotracker.utils import get_last_price
from datetime import datetime

from django.db.models import Max



def save_pool_balance(address, pool, token, quantity):
    """
    Saves the pool balance to the database.
    Args:
        pool (Pool): The pool object.
        token (Cryptocurrency): The cryptocurrency object.
        quantity (float): The quantity of the token.
    """
    pool_balance = PoolBalance(
        address=Address.objects.get(public_address=address),
        pool=pool,
        token=token,
        quantity=quantity,
        snapshot_date=datetime.now(),
    )
    pool_balance.save()

def save_pool_rewards(address, pool, token, quantity):
    """
    Saves the pool rewards to the database.
    Args:
        pool (Pool): The pool object.
        token (Cryptocurrency): The cryptocurrency object.
        quantity (float): The quantity of the token.
    """
    pool_rewards = PoolRewards(
        address= Address.objects.get(public_address=address),
        pool=pool,
        token=token,
        quantity=quantity,
        snapshot_date=datetime.now(),
    )
    pool_rewards.save()

def update_protocols_snapshots(address: str):
    """
    Updates the snapshots of the protocols in the database.
    This function iterates through all the protocols and their pools, fetching the data from the blockchain
    and saving it to the database.
    """
    update_lqty_v1_staking(address)
    update_lqty_v2_staking(address)
    update_lqty_stability_pool(address)
    update_lqty_stability_pool_v2(address)
    update_aave_lending_pool_data(address)

def get_protocols_snapshots(addresses: list, protocol_name: srt) -> dict:
    """
    Fetches the last snapshot of the protocols in the database.
    This function iterates through all the protocols and their pools, fetching the data from the database           
    and returning it as a dictionary.
    """
    last_pool_data = {}
    protocols = Protocol.objects.get(name=protocol_name)
    for protocol in protocols:
        
        pools_balances = PoolBalance.objects.filter(address__in=addresses, pool__protocol=protocol)
        pools_rewards = PoolRewards.objects.filter(addres__in=addresses, pool__protocol=protocol)
        if not pools_balances:
            continue
        
        pools = Pool.objects.filter(protocol=protocol)
        for pool in pools:
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
                snapshot_date__in=[entry["latest_balance_date"] for entry in latest_balances]
            )
            last_rewards = pool_rewards.filter(
                snapshot_date__in=[entry["latest_rewards_date"] for entry in latest_rewards]
            )
            last_pool_data[pool.name] = {
                "balances": {},
                "rewards": {},
            }
            for balance in last_balances:
                current_price = get_last_price(
                        balance.token.name, balance.snapshot_date.date()
                    )
                last_pool_data[protocol.name][pool.name]["balances"][balance.token.name] = {
                    "network": balance.token.network.name,
                    "quantity": balance.quantity,
                    "balance_eur": balance.quantity * current_price,
                    "image": balance.token.image,
                }
            for reward in last_rewards:
                last_pool_data[protocol.name][pool.name]["rewards"][reward.token.name] = {
                    "quantity": reward.quantity,
                }
    return last_pool_data



