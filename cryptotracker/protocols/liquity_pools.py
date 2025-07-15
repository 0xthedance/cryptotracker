import logging
from ape import Contract, networks
from decimal import Decimal

from cryptotracker.models import (
    Pool,
    Snapshot,
    UserAddress,
    Cryptocurrency,
    Trove,
    TroveSnapshot,
)
from cryptotracker.constants import (
    NETWORKS,
    POOL_TYPES,
    TOKENS,
    PROTOCOLS_DATA,
    ETHEREUM_RPC,
)
from cryptotracker.protocols.protocols import save_pool_snapshot
from cryptotracker.protocols.subgraph import send_graphql_query
from cryptotracker.utils import get_last_price

LQTY_V2_SUBGRAPH_ID = "6bg574MHrEZXopJDYTu7S7TAvJKEMsV111gpKLM7ZCA7"


def get_proxy_staking_contract(user_address: UserAddress) -> str:
    LQTY_V2_STAKING = Pool.objects.get(
        type__name=POOL_TYPES["STAKING"],
        protocol_network__protocol__name=PROTOCOLS_DATA["LQTY_V2"]["name"],
        protocol_network__network__name=NETWORKS["ETHEREUM"]["name"],
    )

    with networks.parse_network_choice(ETHEREUM_RPC):
        lqty_govern_contract = Contract(LQTY_V2_STAKING.contract_address)
        return lqty_govern_contract.deriveUserProxyAddress(user_address.public_address)


def get_lqty_stakes(
    address: str, pool: Pool, snapshot: Snapshot, user_address: UserAddress
) -> None:
    """
    Helper to query the LQTY stakes of a given public user_address using the staking pool v1 and save the snapshot
    Args:
        address (str): The address to check the stakes ( a proxy address in LQTY v2 and user address in LQTY v1).
        pool (Pool): The pool object to save the snapshot.
        snapshot (Snapshot): The snapshot object to associate with the updates.
        user_address (UserAddress): The user_address object to associate with the updates.
    """
    LQTY_V1_STAKING = Pool.objects.get(
        type__name=POOL_TYPES["STAKING"],
        protocol_network__protocol__name=PROTOCOLS_DATA["LQTY_V1"]["name"],
        protocol_network__network__name=NETWORKS["ETHEREUM"]["name"],
    )

    with networks.parse_network_choice(ETHEREUM_RPC):
        contract = Contract(LQTY_V1_STAKING.contract_address)
        lqty_stakes = contract.stakes(address)
        if not lqty_stakes:
            return
        eth_rewards = contract.getPendingETHGain(address)
        lusd_rewards = contract.getPendingLUSDGain(address)

    save_pool_snapshot(
        pool=pool,
        address=user_address,
        token_symbol="LQTY",
        quantity=lqty_stakes / 1e18,
        snapshot=snapshot,
    )
    # Save PoolRewardsSnapshot
    save_pool_snapshot(
        pool=pool,
        address=user_address,
        token_symbol="ETH",
        quantity=eth_rewards / 1e18,
        snapshot=snapshot,
        is_reward=True,
    )
    save_pool_snapshot(
        pool=pool,
        address=user_address,
        token_symbol="LUSD",
        quantity=lusd_rewards / 1e18,
        snapshot=snapshot,
        is_reward=True,
    )


def update_lqty_v1_staking(user_address: UserAddress, snapshot: Snapshot) -> None:
    """
    Saves a snapshot of the total LQTY v1 stakes of a given user_address.
    Args:
        user_address (UserAddress): The user_address to check.
        snapshot (Snapshot): The snapshot object to associate with the updates.
    """
    logging.info("Updating LQTY V1 staking")
    LQTY_V1_STAKING = Pool.objects.get(
        type__name=POOL_TYPES["STAKING"],
        protocol_network__protocol__name=PROTOCOLS_DATA["LQTY_V1"]["name"],
        protocol_network__network__name=NETWORKS["ETHEREUM"]["name"],
    )
    get_lqty_stakes(
        user_address.public_address, LQTY_V1_STAKING, snapshot, user_address
    )


def update_lqty_v2_staking(user_address: UserAddress, snapshot: Snapshot) -> None:
    """
    Saves the total LQTY V2 governance stakes of a given user_address.
    Args:
        user_address (UserAddress): The user_address to check.
    """
    logging.info("Updating LQTY V2 staking")

    LQTY_V2_STAKING = Pool.objects.get(
        type__name=POOL_TYPES["STAKING"],
        protocol_network__protocol__name=PROTOCOLS_DATA["LQTY_V2"]["name"],
        protocol_network__network__name=NETWORKS["ETHEREUM"]["name"],
    )

    proxy_contract = get_proxy_staking_contract(user_address)
    logging.info(f"Proxy contract for {user_address.public_address}: {proxy_contract}")
    get_lqty_stakes(proxy_contract, LQTY_V2_STAKING, snapshot, user_address)


def update_lqty_stability_pool(user_address: UserAddress, snapshot: Snapshot) -> None:
    """
    Saves the LQTY V1 stability pool participation of a given user_address.
    Args:
        user_address (str): The user_address to check.
    """
    logging.info(" Updating LQTY V1 stability pool")

    LQTY_V1_STABILITY_POOL = Pool.objects.get(
        type__name=POOL_TYPES["STABILITY_POOL"],
        protocol_network__protocol__name=PROTOCOLS_DATA["LQTY_V1"]["name"],
        protocol_network__network__name=NETWORKS["ETHEREUM"]["name"],
    )

    with networks.parse_network_choice(ETHEREUM_RPC):
        contract = Contract(LQTY_V1_STABILITY_POOL.contract_address)
        deposits = contract.deposits(user_address.public_address)
        if not deposits.initialValue:
            return
        ETH_gains = contract.getDepositorETHGain(user_address.public_address)
        LQTY_gains = contract.getDepositorLQTYGain(user_address.public_address)

    # Save PoolBalanceSnapshot
    save_pool_snapshot(
        pool=LQTY_V1_STABILITY_POOL,
        address=user_address,
        token_symbol="LUSD",
        quantity=deposits.initialValue / 1e18,
        snapshot=snapshot,
    )
    # Save PoolRewardsSnapshot
    save_pool_snapshot(
        pool=LQTY_V1_STABILITY_POOL,
        address=user_address,
        token_symbol="ETH",
        quantity=ETH_gains / 1e18,
        snapshot=snapshot,
        is_reward=True,
    )
    save_pool_snapshot(
        pool=LQTY_V1_STABILITY_POOL,
        address=user_address,
        token_symbol="LQTY",
        quantity=LQTY_gains / 1e18,
        snapshot=snapshot,
        is_reward=True,
    )


def update_lqty_stability_pool_v2(
    user_address: UserAddress, snapshot: Snapshot
) -> None:
    """
    Saves a snapshot of the participation of a given user_address in the three LIQUITY V2 stabiity pools .
    Args:
        user_address (str): The user_address to check.
    """
    logging.info("Updating LQTY V2 stability pool")

    LQTY_V2_STABILITY_POOLS = Pool.objects.filter(
        type__name=POOL_TYPES["STABILITY_POOL"],
        protocol_network__protocol__name=PROTOCOLS_DATA["LQTY_V2"]["name"],
        protocol_network__network__name=NETWORKS["ETHEREUM"]["name"],
    )

    with networks.parse_network_choice(ETHEREUM_RPC):
        for pool in LQTY_V2_STABILITY_POOLS:
            contract = Contract(pool.contract_address)
            deposits = contract.deposits(user_address.public_address)
            if not deposits:
                continue
            coll_gains = contract.getDepositorCollGain(user_address.public_address)
            yield_gains = contract.getDepositorYieldGain(user_address.public_address)

            # Save PoolBalanceSnapshot
            save_pool_snapshot(
                pool=pool,
                address=user_address,
                token_symbol="BOLD",
                quantity=deposits / 1e18,
                snapshot=snapshot,
            )
            # Save PoolRewardsSnapshot gains (BOLD) and collateral (WETH, wstETH, and rETH)
            save_pool_snapshot(
                pool=pool,
                address=user_address,
                token_symbol="BOLD",
                quantity=yield_gains / 1e18,
                snapshot=snapshot,
                is_reward=True,
            )

            token_symbol = pool.description
            if not token_symbol:
                continue

            save_pool_snapshot(
                pool=pool,
                address=user_address,
                token_symbol=token_symbol,
                quantity=coll_gains / 1e18,
                snapshot=snapshot,
                is_reward=True,
            )


def get_troves(user_address: UserAddress, snapshot: Snapshot) -> None:
    """Query all the troves for a given user_address using The Graph API"""

    pool = Pool.objects.get(
        type__name=POOL_TYPES["BORROWING"],
        protocol_network__protocol__name=PROTOCOLS_DATA["LQTY_V2"]["name"],
        protocol_network__network__name=NETWORKS["ETHEREUM"]["name"],
    )
    query = f"""
    {{
        troves(
            where: {{
                borrower: "{user_address.public_address}",
                status_in: ["active"]
            }}
            orderBy: updatedAt
            orderDirection: desc
        ) {{
            createdAt
            deposit
            collateral {{
                collIndex
            }}
            interestRate
            debt
            id
        }}
    }}
    """
    logging.info("Fetching troves for user: %s", user_address.public_address)
    troves = send_graphql_query(LQTY_V2_SUBGRAPH_ID, query)
    if not troves or not troves.get("data") or not troves["data"].get("troves"):
        return

    for trove in troves["data"]["troves"]:
        token = Cryptocurrency.objects.get(
            symbol={
                0: "WETH",
                1: "wstETH",
            }.get(trove["collateral"]["collIndex"], "rETH")
        )

        logging.info(
            f"Processing trove {trove['id']} for user {user_address.public_address}"
        )

        trove_obj, _ = Trove.objects.get_or_create(
            trove_id=trove["id"],
            defaults={
                "user_address": user_address,
                "pool": pool,
                "token": token,
            },
        )
        collateral = Decimal(trove["deposit"]) / Decimal(1e18)
        debt = Decimal(trove["debt"]) / Decimal(1e18)

        collateral_eur = collateral * get_last_price(token.name, snapshot.date)

        debt_eur = debt * get_last_price(TOKENS["BOLD"]["name"], snapshot.date)
        balance = collateral_eur - debt_eur

        TroveSnapshot.objects.create(
            trove=trove_obj,
            collateral=collateral,
            debt=debt,
            balance=balance,
            interest_rate=Decimal(trove["interestRate"]) / Decimal(1e16),
            snapshot=snapshot,
        )


def update_lqty_pools(user_address: UserAddress, snapshot: Snapshot) -> None:
    """
    Updates the snapshots of the LQTY pools participation for a given user_address.
    Args:
        user_address (UserAddress): The user_address to check.
        snapshot (Snapshot): The snapshot object to associate with the updates.
    """
    update_lqty_stability_pool(user_address, snapshot)
    update_lqty_stability_pool_v2(user_address, snapshot)
    update_lqty_v1_staking(user_address, snapshot)
    update_lqty_v2_staking(user_address, snapshot)
    get_troves(user_address, snapshot)
