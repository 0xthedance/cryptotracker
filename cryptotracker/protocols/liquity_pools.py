from ape import Contract, networks

from cryptotracker.models import Pool, Snapshot, UserAddress, Cryptocurrency, Trove, TroveSnapshot, PoolType
from cryptotracker.constants import NETWORKS,POOL_TYPES,PROTOCOLS
from cryptotracker.protocols.protocols import save_pool_snapshot
from cryptotracker.protocols.subgraph import send_graphql_query
from cryptotracker.utils import get_last_price




def get_proxy_staking_contract(user_address: UserAddress) -> str:

    LQTY_V2_STAKING =Pool.objects.get(
        type__name=POOL_TYPES["STAKING"],
        protocol_network__protocol__name=PROTOCOLS["LIQUITY V2"],
        protocol_network__network__name=NETWORKS["ETHEREUM"],
    )

    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        lqty_govern_contract = Contract(LQTY_V2_STAKING.contract_address)
        return lqty_govern_contract.deriveUserProxyAddress(user_address.public_address)


def get_lqty_stakes(address: str, pool: Pool, snapshot: Snapshot, user_address: UserAddress) -> None:
    """
    Helper to query the LQTY stakes of a given public user_address using the staking pool v1 and save the snapshot
    Args:
        public_address (str): The user_address to check.
    """
    LQTY_V1_STAKING =Pool.objects.get(
        type__name=POOL_TYPES["STAKING"],
        protocol_network__protocol__name=PROTOCOLS["LIQUITY V1"],
        protocol_network__network__name=NETWORKS["ETHEREUM"],
    )
    
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        contract = Contract(LQTY_V1_STAKING.contract_address)
        lqty_stakes = contract.stakes(address)
        if not lqty_stakes:
            return
        eth_rewards = contract.getPendingETHGain(address)
        lusd_rewards = contract.getPendingLUSDGain(address)
    
    save_pool_snapshot(
        pool,
        user_address,
        "LQTY",
        lqty_stakes / 1e18,
        snapshot,
    )
    # Save PoolRewardsSnapshot
    save_pool_snapshot(
        pool,
        user_address,
        "ETH",
        eth_rewards / 1e18,
        snapshot,
        True,
    )
    save_pool_snapshot(
        pool,
        user_address,
        "LUSD",
        lusd_rewards / 1e18,
        snapshot,
        True,
    )


def update_lqty_v1_staking(
    user_address: UserAddress, snapshot:Snapshot
) -> None: 
    """
    Saves a snapshot of the total LQTY v1 stakes of a given user_address.
    Args:
        user_address (str): The user_address to check.
    """
    print("update_lqty_staking")
    LQTY_V1_STAKING =Pool.objects.get(
        type__name=POOL_TYPES["STAKING"],
        protocol_network__protocol__name=PROTOCOLS["LIQUITY V1"],
        protocol_network__network__name=NETWORKS["ETHEREUM"],
    )
    get_lqty_stakes(user_address.public_address, LQTY_V1_STAKING, snapshot, user_address)


def update_lqty_v2_staking(user_address: UserAddress, snapshot: Snapshot) -> None:
    """
    Saves the total LQTY V2 governance stakes of a given user_address.
    Args:
        user_address (UserAddress): The user_address to check.
    """
    print("update_lqty_staking_v2")

    LQTY_V2_STAKING =Pool.objects.get(
        type__name=POOL_TYPES["STAKING"],
        protocol_network__protocol__name=PROTOCOLS["LIQUITY V2"],
        protocol_network__network__name=NETWORKS["ETHEREUM"],
    )

    proxy_contract = get_proxy_staking_contract(user_address)
    print("get stakes")
    get_lqty_stakes(proxy_contract, LQTY_V2_STAKING, snapshot, user_address)



def update_lqty_stability_pool(user_address: UserAddress, snapshot: Snapshot) -> None:
    """
    Saves the LQTY V1 stability pool participation of a given user_address.
    Args:
        user_address (str): The user_address to check.
    """
    print("update_lqty_stability_pool_v1")

    LQTY_V1_STABILITY_POOL =Pool.objects.get(
        type__name=POOL_TYPES["STABILITY_POOL"],
        protocol_network__protocol__name=PROTOCOLS["LIQUITY V1"],
        protocol_network__network__name=NETWORKS["ETHEREUM"],
    )
    print(LQTY_V1_STABILITY_POOL)

    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        contract = Contract(LQTY_V1_STABILITY_POOL.contract_address)
        deposits = contract.deposits(user_address.public_address)
        if not deposits.initialValue:
            return
        ETH_gains = contract.getDepositorETHGain(user_address.public_address)
        LQTY_gains = contract.getDepositorLQTYGain(user_address.public_address)

    print("Saving")
    # Save PoolBalanceSnapshot
    save_pool_snapshot(
        LQTY_V1_STABILITY_POOL,
        user_address,
        "LUSD",
        deposits.initialValue / 1e18,
        snapshot,
    )
    # Save PoolRewardsSnapshot
    save_pool_snapshot(
        LQTY_V1_STABILITY_POOL,
        user_address,
        "ETH",
        ETH_gains / 1e18,
        snapshot,
        True,
    )
    save_pool_snapshot(
        LQTY_V1_STABILITY_POOL,
        user_address,
        "LQTY",
        LQTY_gains / 1e18,
        snapshot,
        True,
    )


def update_lqty_stability_pool_v2(user_address: UserAddress, snapshot: Snapshot) -> None:
    """
    Saves a snapshot of the participation of a given user_address in the three LIQUITY V2 stabiity pools .
    Args:
        user_address (str): The user_address to check.
    """
    print("update_lqty_stability_pool_v2")

    LQTY_V2_STABILITY_POOLS =Pool.objects.filter(
        type__name=POOL_TYPES["STABILITY_POOL"],
        protocol_network__protocol__name=PROTOCOLS["LIQUITY V2"],
        protocol_network__network__name=NETWORKS["ETHEREUM"],
    )

    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        for pool in LQTY_V2_STABILITY_POOLS:
            contract = Contract(pool.contract_address)
            deposits = contract.deposits(user_address.public_address)
            print(deposits)
            if not deposits:
                continue
            coll_gains = contract.getDepositorCollGain(user_address.public_address)
            yield_gains = contract.getDepositorYieldGain(user_address.public_address)

            # Save PoolBalanceSnapshot
            save_pool_snapshot(
                pool,
                user_address,
                "BOLD",
                deposits / 1e18,
                snapshot,
            )
            # Save PoolRewardsSnapshot gains (BOLD) and collatera (WETH, wstETH and rETH )
            save_pool_snapshot(
                pool,
                user_address,
                "BOLD",
                yield_gains / 1e18,
                snapshot,
                True,
            )
            token_symbol =  pool.description
            print(token_symbol)
            save_pool_snapshot(
                pool,
                user_address,
                token_symbol,
                coll_gains / 1e18,
                snapshot,
                True,
            )



LQTY_V2_SUBGRAPH_ID = "6bg574MHrEZXopJDYTu7S7TAvJKEMsV111gpKLM7ZCA7"


def get_troves(user_address: UserAddress, snapshot: Snapshot) -> None:
    """Query all the troves for a given user_address using The Graph API"""

    pool =Pool.objects.get(
            type__name=POOL_TYPES["BORROW"],
            protocol_network__protocol__name=PROTOCOLS["LIQUITY V2"],
            protocol_network__network__name=NETWORKS["ETHEREUM"],
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

        trove_obj, _ = Trove.objects.get_or_create(
            trove_id=trove["id"],
            defaults={
                "user_address": user_address,
                "pool": pool,
                "token": token,
            },
        )
        collateral = int(trove["deposit"]) / 1e18
        debt=int(trove["debt"]) / 1e18

        collateral_eur = collateral * get_last_price(token.name,snapshot.date)
        debt_eur = debt * get_last_price("liquity-bold",snapshot.date)
        balance = (collateral_eur - debt_eur)

        TroveSnapshot.objects.create(
            trove=trove_obj,
            collateral=collateral,
            debt=debt,
            balance = balance,
            interest_rate=int(trove["interestRate"]) / 1e16,
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
