from decimal import Decimal
from typing import List

from cryptotracker.models import (
    Snapshot,
    PoolPosition,
    PoolBalanceSnapshot,
    PoolRewardsSnapshot,
    Cryptocurrency,
    PoolPosition,
    UserAddress,
    TroveSnapshot,
    Protocol,
    Pool,
)

from cryptotracker.utils import get_last_price

from typing import Optional

from collections import defaultdict

def save_pool_snapshot(
    pool: Pool,
    address: UserAddress,
    token_symbol: Cryptocurrency,
    quantity: Decimal,
    snapshot: Snapshot,
    is_reward: bool = False,
    pool_id: int = None,
    )-> None:
    """
    Saves the pool balance or rewards to the database.
    Args:
        pool_position (PoolPosition): Pool Position
        pool_id (int, optional): The ID of the pool (default: None).
        token (Cryptocurrency): The cryptocurrency object.
        quantity (Decimal): The quantity of the token.
        snapshot (Snapshot): The snapshot object.
        is_reward (bool): Whether the data is a reward (default: False).
    """
    try:

        token = Cryptocurrency.objects.get(symbol=token_symbol)

        pool_position, created = PoolPosition.objects.get_or_create(
            user_address=address,
            pool=pool,
            defaults={"pool_id": pool_id} if pool_id else {}
        )
        print(pool_position)

        # Dynamically choose the snapshot model
        snapshot_model = PoolRewardsSnapshot if is_reward else PoolBalanceSnapshot

        pool_snapshot = snapshot_model(
            pool_position=pool_position,
            token=token,
            quantity=quantity,
            snapshot=snapshot,
        )

        print(pool_snapshot)
        pool_snapshot.save()
    except Exception as e:
        print(f"Error saving pool {pool} {'reward' if is_reward else 'balance'}: {e}")

class PoolData:
    def __init__(self, pool_position: PoolPosition, snapshot: Snapshot):
        """
        Initialize PoolData with a pool position and snapshot.
        """
        self.pool_position = pool_position
        self.snapshot = snapshot
        self.protocol = self._protocol()
        self.balances = self._get_balance()
        self.rewards = self._get_rewards()
        self.balance_eur = self._calculate_balance_eur() 

    def _protocol(self)-> Protocol:
        return self.pool_position.pool.protocol_network.protocol.name
    
    def _get_balance(self) -> List[PoolBalanceSnapshot]:
        """
        Fetch the balance snapshot for the pool position and snapshot.
        """
        try:
            return PoolBalanceSnapshot.objects.filter(
                pool_position=self.pool_position, snapshot=self.snapshot
            )
        except PoolBalanceSnapshot.DoesNotExist:
            print(ValueError(f"No balance found for pool {self.pool_position} in snapshot {self.snapshot}"))
            return None

    def _get_rewards(self) -> List[PoolRewardsSnapshot]:
        """
        Fetch the rewards snapshots for the pool position and snapshot.
        """
        try:
            return PoolRewardsSnapshot.objects.filter(
                    pool_position=self.pool_position, snapshot=self.snapshot
                )
        except PoolBalanceSnapshot.DoesNotExist:
            print(ValueError(f"No balance found for pool {self.pool_position} in snapshot {self.snapshot}"))
            return None

    def _calculate_balance_eur(self) -> Decimal:
        """
        Calculate the balance in EUR based on the current price.
        """
        if not self.balances:
            return None
        balance_eu = 0
        for balance in self.balances:
            print(balance, "balance")
            current_price = get_last_price(balance.token.name, self.snapshot.date)
            balance_eu +=balance.quantity * current_price
        
        return balance_eu


def get_protocols_snapshots(user_addresses: list) -> Optional[dict]:
    """
    Fetches the last snapshot of the protocols in the database.

    """
    last_snapshot = Snapshot.objects.first()

    user_pools = PoolPosition.objects.filter(user_address__in = user_addresses)

    if not user_pools:
        return

    pool_data = []

    for pool in user_pools:
        data = PoolData(pool, last_snapshot)
        if data.balances:
            pool_data.append(data)
    
    troves = TroveSnapshot.objects.filter(
        trove__user_address__in=user_addresses,
        snapshot=last_snapshot,
    )
    print(troves, "troves")

    grouped_data = defaultdict(list)

    for pool in pool_data:
        protocol_name = pool.protocol
        grouped_data[protocol_name].append(pool)

    grouped_data = dict(grouped_data)

    return {
         "pool_data": grouped_data,
         "troves": troves,
    }







    '''
    PROTOCOLS = ["Liquity V1","Liquity V2","Aave V3", "Uniswap V3"]

    last_protocol_data = {}

    for protocol_name in PROTOCOLS:
        last_pool_data: dict = {}
        protocols = ProtocolNetwork.objects.filter(protocol__name=protocol_name)
        last_snapshot = Snapshot.objects.first()
        if not last_snapshot:
            return {}
        for protocol in protocols:
            pools_balances = PoolBalanceSnapshot.objects.filter(
                address__in=user_addresses, pool__protocol_network=protocol
            )
            pools_rewards = PoolRewardsSnapshot.objects.filter(
                address__in=user_addresses, pool__protocol_network=protocol
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
                        trove__address__in=user_addresses,
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
'''
