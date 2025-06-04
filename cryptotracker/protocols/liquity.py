from ape import Contract, networks
from cryptotracker.models import (
    Pool,
    ProtocolNetwork,
    Cryptocurrency,
    Trove,
    TroveSnapshot,
    Address,
    Snapshot
)
from cryptotracker.protocols.protocols import save_pool_balance, save_pool_rewards
from cryptotracker.protocols.subgraph import send_graphql_query

ETH_NETWORK_NAME = "Ethereum"

LIQUITY_V2 ="Liquity V2"

LIQUITY_V1 ="Liquity V1"

LQTY_V2_SUBGRAPH_ID = "6bg574MHrEZXopJDYTu7S7TAvJKEMsV111gpKLM7ZCA7"


def get_troves(address: Address, snapshot: Snapshot) -> None:
    """Query all the troves for a given address using The Graph API"""

    query = f"""
    {{
        troves(
            where: {{
                borrower: "{address.public_address}",
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

    protocol = ProtocolNetwork.objects.get(
        protocol__name=LIQUITY_V2, network__name=ETH_NETWORK_NAME
    )

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
                "address": address,
                "pool": Pool.objects.get(protocol_network=protocol, name="borrow"),
                "token": token,
            },
        )

        TroveSnapshot.objects.create(
            trove=trove_obj,
            collateral=int(trove["deposit"]) / 1e18,
            debt=int(trove["debt"]) / 1e18,
            interest_rate=int(trove["interestRate"]) / 1e16,
            snapshot=snapshot,
        )


def get_proxy_staking_contract(address: Address) -> str:
    protocol = ProtocolNetwork.objects.get(
        protocol__name=LIQUITY_V2, network__name=ETH_NETWORK_NAME
    )
    pool = Pool.objects.get(
        protocol_network=protocol,
        name="staking",
    )
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        lqty_govern_contract = Contract(pool.address)
        return lqty_govern_contract.deriveUserProxyAddress(address.public_address)


def get_lqty_stakes(public_address: str) -> dict:
    """
    Returns the LQTY stakes of a given public address using the staking pool v1.
    Args:
        public_address (str): The address to check.
    Returns:
        dict: A dictionary with LQTY stakes information.
    """
    protocol = ProtocolNetwork.objects.get(
        protocol__name=LIQUITY_V1, network__name=ETH_NETWORK_NAME
    )
    pool = Pool.objects.get(
        protocol_network=protocol,
        name="staking",
    )
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        contract = Contract(pool.address)
        lqty_stakes = contract.stakes(public_address)
        if not lqty_stakes:
            return {}
        eth_rewards = contract.getPendingETHGain(public_address)
        lusd_rewards = contract.getPendingLUSDGain(public_address)
        return {
            "lqty_stakes": lqty_stakes / 1e18,
            "eth_rewards": eth_rewards / 1e18,
            "lusd_rewards": lusd_rewards / 1e18,
        }


def update_lqty_pools(address: Address, snapshot: Snapshot) -> None:
    """
    Updates the snapshots of the LQTY pools participation for a given address.
    Args:
        address (Address): The address to check.
        snapshot (Snapshot): The snapshot object to associate with the updates.
    """
    update_lqty_stability_pool(address, snapshot)
    update_lqty_stability_pool_v2(address, snapshot)
    update_lqty_v1_staking(address, snapshot)
    update_lqty_v2_staking(address, snapshot)
    get_troves(address, snapshot)


def update_lqty_v1_staking(
    address: Address, snapshot:Snapshot
) -> None:  # TODO: Solve the duplication between LQTYV1 stakes and LQTY V2 stakes
    """
    Saves a snapshot of the total LQTY v1 stakes of a given address.
    Args:
        address (str): The address to check.
    """
    print("update_lqty_staking")
    lqty_staking = get_lqty_stakes(address.public_address)
    if lqty_staking:
        # Save PoolBalance
        protocol = ProtocolNetwork.objects.get(
            protocol__name=LIQUITY_V1, network__name=ETH_NETWORK_NAME
        )
        pool = Pool.objects.get(
            protocol_network=protocol,
            name="staking",
        )
        save_pool_balance(
            address,
            pool,
            Cryptocurrency.objects.get(name="LQTY"),
            lqty_staking["lqty_stakes"],
            snapshot,
        )
        # Save PoolRewards
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(name="ETH"),
            lqty_staking["eth_rewards"],
            snapshot,
        )
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(name="LUSD"),
            lqty_staking["lusd_rewards"],
            snapshot,
        )


def update_lqty_v2_staking(address: Address, snapshot: Snapshot) -> None:
    """
    Saves the total LQTY V2 governance stakes of a given address.
    Args:
        address (Address): The address to check.
    """
    print("update_lqty_staking_v2")

    proxy_contract = get_proxy_staking_contract(address)
    lqty_staking = get_lqty_stakes(proxy_contract)
    if lqty_staking:
        # Save PoolBalance
        protocol = ProtocolNetwork.objects.get(
            protocol__name=LIQUITY_V1, network__name=ETH_NETWORK_NAME
        )

        pool = Pool.objects.get(
            protocol_network=protocol,
            name="staking",
        )
        save_pool_balance(
            address,
            pool,
            Cryptocurrency.objects.get(symbol="LQTY"),
            lqty_staking["lqty_stakes"],
            snapshot,
        )
        # Save PoolRewards
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(symbol="ETH"),
            lqty_staking["eth_rewards"],
            snapshot,
        )
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(symbol="LUSD"),
            lqty_staking["lusd_rewards"],
            snapshot,
        )


def update_lqty_stability_pool(address: Address, snapshot: Snapshot) -> None:
    """
    Saves the LQTY V1 stability pool participation of a given address.
    Args:
        address (str): The address to check.
    """
    print("update_lqty_stability_pool_v1")
    protocol = ProtocolNetwork.objects.get(
        protocol__name=LIQUITY_V1, network__name=ETH_NETWORK_NAME
    )
    pool = Pool.objects.get(
        protocol_network=protocol,
        name="stability pool",
    )
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        contract = Contract(pool.address)
        deposits = contract.deposits(address.public_address)
        if not deposits.initialValue:
            return
        ETH_gains = contract.getDepositorETHGain(address.public_address)
        LQTY_gains = contract.getDepositorLQTYGain(address.public_address)

        # Save PoolBalance
        save_pool_balance(
            address,
            pool,
            Cryptocurrency.objects.get(symbol="LUSD"),
            deposits.initialValue / 1e18,
            snapshot,
        )
        # Save PoolRewards
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(symbol="ETH"),
            ETH_gains / 1e18,
            snapshot,
        )
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(symbol="LQTY"),
            LQTY_gains / 1e18,
            snapshot,
        )


def update_lqty_stability_pool_v2(address: Address, snapshot: Snapshot) -> None:
    """
    Saves a snapshot of the participation of a given address in the three LIQUITY V2 stabiity pools .
    Args:
        address (str): The address to check.
    """
    print("update_lqty_stability_pool_v2")
    protocol = ProtocolNetwork.objects.get(
        protocol__name=LIQUITY_V2, network__name=ETH_NETWORK_NAME
    )
    pools = Pool.objects.filter(
        protocol_network=protocol,
        name__contains="stability pool",
    )
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        for pool in pools:
            contract = Contract(pool.address)
            deposits = contract.deposits(address.public_address)
            print(deposits)
            if not deposits:
                continue
            coll_gains = contract.getDepositorCollGain(address.public_address)
            yield_gains = contract.getDepositorYieldGain(address.public_address)

            # Save PoolBalance
            save_pool_balance(
                address,
                pool,
                Cryptocurrency.objects.get(symbol="BOLD"),
                deposits / 1e18,
                snapshot,
            )

            # Save PoolRewards gains (BOLD) and collatera (WETH, wstETH and rETH )
            save_pool_rewards(
                address,
                pool,
                Cryptocurrency.objects.get(symbol="BOLD"),
                yield_gains / 1e18,
                snapshot,
            )
            token = Cryptocurrency.objects.get(
                symbol={
                    "stability pool WETH": "WETH",
                    "stability pool wstETH": "wstETH",
                }.get(pool.name, "rETH")
            )
            save_pool_rewards(
                address,
                pool,
                token,
                coll_gains / 1e18,
                snapshot,
            )
