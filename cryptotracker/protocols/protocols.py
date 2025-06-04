from decimal import Decimal

from cryptotracker.models import (
    Snapshot,
    Pool,
    ProtocolNetwork,
    PoolBalance,
    PoolRewards,
    Address,
    TroveSnapshot,
    Cryptocurrency,
)

from cryptotracker.utils import get_last_price



def save_pool_balance(address: Address, pool: Pool, token: Cryptocurrency, quantity: Decimal, snapshot: Snapshot):
    """
    Saves the pool balance to the database.
    Args:
        pool (Pool): The pool object.
        token (Cryptocurrency): The cryptocurrency object.
        quantity (float): The quantity of the token.
    """
    try:
        pool_balance = PoolBalance(
            address=address,
            pool=pool,
            token=token,
            quantity=quantity,
            snapshot=snapshot,
        )
        print(pool_balance)

        pool_balance.save()
    except Exception as e:
        print(f"Error saving pool {pool.name} balance: {e}")


def save_pool_rewards(address: Address, pool: Pool, token: Cryptocurrency, quantity: Decimal, snapshot: Snapshot):
    """
    Saves the pool rewards to the database.
    Args:
        pool (Pool): The pool object.
        token (Cryptocurrency): The cryptocurrency object.
        quantity (float): The quantity of the token.
    """
    pool_rewards = PoolRewards(
        address=address,
        pool=pool,
        token=token,
        quantity=quantity,
        snapshot=snapshot,
    )
    print(pool_rewards)
    pool_rewards.save()


def get_protocols_snapshots(addresses: list) -> dict:
    """
    Fetches the last snapshot of the protocols in the database.
    This function iterates through all the protocols and their pools, fetching the data from the database
    and returning it as a dictionary.
        total_liquity_v1 = get_protocols_snapshots(addresses, protocol_name="Liquity V1")
    total_liquity_v2 = get_protocols_snapshots(addresses, protocol_name="Liquity V2")
    total_aave = get_protocols_snapshots(addresses, protocol_name="Aave V3")
    """
    PROTOCOLS = ["Liquity V1","Liquity V2","Aave V3", "Uniswap V3"]

    last_protocol_data = {}

    for protocol_name in PROTOCOLS:
        last_pool_data: dict = {}
        protocols = ProtocolNetwork.objects.filter(protocol__name=protocol_name)
        last_snapshot = Snapshot.objects.first()
        if not last_snapshot:
            return {}
        for protocol in protocols:
            pools_balances = PoolBalance.objects.filter(
                address__in=addresses, pool__protocol_network=protocol
            )
            pools_rewards = PoolRewards.objects.filter(
                address__in=addresses, pool__protocol_network=protocol
            )
            if not pools_balances:
                continue

            pools = Pool.objects.filter(protocol_network=protocol)
            for pool in pools:
                last_pool_data[pool.name] = {
                    "balances": {},
                    "rewards": {},
                    "troves": [],
                }

                if pool.name == "borrow":
                    troves = TroveSnapshot.objects.filter(
                        trove__address__in=addresses,
                        trove__pool=pool,
                        snapshot=last_snapshot,
                    )
                    if not troves:
                        continue
                    last_pool_data[pool.name]["troves"].append(troves)
                    continue

                last_pool_balances = pools_balances.filter(
                    pool=pool, snapshot=last_snapshot
                )
                if not last_pool_balances:
                    continue

                for balance in last_pool_balances:
                    current_price = get_last_price(
                        balance.token.name, last_snapshot.date)
                    last_pool_data[pool.name]["balances"][balance.token.symbol] = {
                        "network": balance.pool.protocol_network.network.name,
                        "quantity": balance.quantity,
                        "balance_eur": balance.quantity * current_price,
                        "image": balance.token.image,
                    }
                last_pool_rewards = pools_rewards.filter(pool=pool, snapshot=last_snapshot)
                if not last_pool_rewards:
                    continue

                for reward in last_pool_rewards:
                    last_pool_data[pool.name]["rewards"][reward.token.symbol] = {
                        "quantity": reward.quantity,
                    }

            if not last_pool_data:
                return None

        last_protocol_data[protocol_name] = last_pool_data
    print(last_protocol_data)
    return last_protocol_data

