import logging

from collections import defaultdict
from decimal import Decimal
from typing import Optional, Dict
from django.db.models import QuerySet

from cryptotracker.models import (
    Cryptocurrency,
    Pool,
    PoolBalanceSnapshot,
    PoolPosition,
    PoolRewardsSnapshot,
    Snapshot,
    TroveSnapshot,
    UserAddress,
)
from cryptotracker.utils import get_last_price


def save_pool_snapshot(
    pool: Pool,
    address: UserAddress,
    token_symbol: str,
    quantity: Decimal,
    snapshot: Snapshot,
    is_reward: bool = False,
    pool_id: Optional[str] = None,
) -> None:
    """
    Saves the pool balance or rewards to the database.
    Args:
        pool_position (PoolPosition): Pool Position
        pool_id (str, optional): The ID of the pool (default: None).
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
            position_id=pool_id,
        )

        if created:
            logging.info(f"Created new pool position: {pool_position}")
        else:
            logging.info(f"Found existing pool position: {pool_position}")

        snapshot_model = PoolRewardsSnapshot if is_reward else PoolBalanceSnapshot

        pool_snapshot = snapshot_model(
            pool_position=pool_position,
            token=token,
            quantity=quantity,
            snapshot=snapshot,
        )

        pool_snapshot.save()
    except Exception as e:
        logging.warning(
            f"Error saving pool {pool} {'reward' if is_reward else 'balance'}: {e}"
        )


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

    def _protocol(self) -> str:
        return self.pool_position.pool.protocol_network.protocol.name

    def _get_balance(self) -> Optional[QuerySet]:
        """
        Fetch the balance snapshot for the pool position and snapshot.
        """
        try:
            return PoolBalanceSnapshot.objects.filter(
                pool_position=self.pool_position, snapshot=self.snapshot
            )
        except PoolBalanceSnapshot.DoesNotExist:
            logging.warning(
                ValueError(
                    f"No balance found for pool {self.pool_position} in snapshot {self.snapshot}"
                )
            )
            return None

    def _get_rewards(self) -> Optional[QuerySet]:
        """
        Fetch the rewards snapshots for the pool position and snapshot.
        """
        try:
            return PoolRewardsSnapshot.objects.filter(
                pool_position=self.pool_position, snapshot=self.snapshot
            )
        except PoolBalanceSnapshot.DoesNotExist:
            logging.warning(
                ValueError(
                    f"No balance found for pool {self.pool_position} in snapshot {self.snapshot}"
                )
            )
            return None

    def _calculate_balance_eur(self) -> Optional[Decimal]:
        """
        Calculate the balance in EUR based on the current price.
        """
        if not self.balances:
            return None
        balance_eu = 0
        for balance in self.balances:
            current_price = get_last_price(balance.token.name, self.snapshot.date)
            balance_eu += balance.quantity * current_price

        return Decimal(balance_eu)


def get_protocols_snapshots(
    user_addresses: list, snapshot: Optional[Snapshot] = None
) -> dict:
    """
    Fetches the last snapshot of the protocols in the database.

    """
    if snapshot is None:
        snapshot = Snapshot.objects.first()

    user_pools = PoolPosition.objects.filter(user_address__in=user_addresses)

    if not user_pools or not snapshot:
        logging.warning("No user pools or last snapshot found.")
        return {"pool_data": {}, "troves": []}

    pool_data = []

    for pool_position in user_pools:
        data = PoolData(pool_position, snapshot)
        if data.balances:
            pool_data.append(data)

    troves = TroveSnapshot.objects.filter(
        trove__user_address__in=user_addresses,
        snapshot=snapshot,
    )

    grouped_data = defaultdict(list)

    for pool in pool_data:
        protocol_name = pool.protocol
        grouped_data[protocol_name].append(pool)

    grouped_data_dict: Dict[str, list[PoolData]] = dict(grouped_data)

    logging.info(f"Grouped data: {grouped_data}")

    return {
        "pool_data": grouped_data_dict,
        "troves": troves,
    }
