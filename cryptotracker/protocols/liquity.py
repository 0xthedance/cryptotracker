from datetime import datetime

from ape import Contract, networks
from cryptotracker.models import (
    Pool,
    ProtocolNetwork,
    Cryptocurrency,
    Trove,
    TroveSnapshot,
    Address,
)
from cryptotracker.protocols.protocols import save_pool_balance, save_pool_rewards
from cryptotracker.protocols.subgraph import send_graphql_query

ETH_NETWORK_NAME = "Ethereum"

THEGRAPH_ID_LQTY= "6bg574MHrEZXopJDYTu7S7TAvJKEMsV111gpKLM7ZCA7"

def get_troves(address: str, snapshot):
    """Query all the troves for a given address using The Graph API"""


    query = f"""
    {{
        troves(
            where: {{
                borrower: "{address}",
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
        protocol__name="Liquity V2", network__name=ETH_NETWORK_NAME
    )

    troves_v2 = send_graphql_query(THEGRAPH_ID_LQTY, query)
    print(troves_v2)

    for trove in troves_v2["data"]["troves"]:
        if trove["collateral"]["collIndex"] == 0:
            token = Cryptocurrency.objects.get(symbol="WETH")
        elif trove["collateral"]["collIndex"] == 1:
            token = Cryptocurrency.objects.get(symbol="wstETH")
        else:
            token = Cryptocurrency.objects.get(symbol="rETH")
    
        trove_obj, created = Trove.objects.get_or_create(
            trove_id=trove["id"],
            defaults={
                "address":Address.objects.get(public_address=address),
                "pool" : Pool.objects.get(protocol_network = protocol, name= "borrow"),
                "token" : token,
            },
        )    

        trove_snapshot = TroveSnapshot(
            trove=trove_obj,
            collateral=int(trove["deposit"]) / 1e18,
            debt=int(trove["debt"]) / 1e18,
            interest_rate=int(trove["interestRate"]) / 1e16,
            snapshot=snapshot,
        )
        trove_snapshot.save()

    # troves_v1 = send_graphql_query(id_lqty_v1, query)


def get_proxy_staking_contract(address: str) -> str:
    protocol = ProtocolNetwork.objects.get(
        protocol__name="Liquity V2", network__name="Ethereum"
    )
    pool = Pool.objects.get(
        protocol_network=protocol,
        name="staking",
    )
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        lqty_govern_contract = Contract(pool.address)
        return lqty_govern_contract.deriveUserProxyAddress(address)


def get_lqty_stakes(address):
    """
    Returns the LQTY  stakes of a given address using the staking pool v1.
    Args:
        address (str): The address to check.
    Returns:
        list: A list of LQTY governance stakes.
    """
    protocol = ProtocolNetwork.objects.get(
        protocol__name="Liquity V1", network__name="Ethereum"
    )
    print(protocol)
    pool = Pool.objects.get(
        protocol_network=protocol,
        name="staking",
    )
    print(pool)
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        contract = Contract(pool.address)
        lqty_stakes = contract.stakes(address)
        if not lqty_stakes:
            return {}
        eth_rewards = contract.getPendingETHGain(address)
        lusd_rewards = contract.getPendingLUSDGain(address)
        lqty_staking = {
            "lqty_stakes": lqty_stakes / 1e18,
            "eth_rewards": eth_rewards / 1e18,
            "lusd_rewards": lusd_rewards / 1e18,
        }
        return lqty_staking


def update_lqty_pools(address, snapshot):
    """
    Updates the snapshots of the LQTY pools participation for a given address.
    Args:
        address (str): The address to check.
    """
    update_lqty_stability_pool(address, snapshot)
    update_lqty_stability_pool_v2(address, snapshot)
    update_lqty_v1_staking(address, snapshot)
    update_lqty_v2_staking(address, snapshot)
    get_troves(address, snapshot)


def update_lqty_v1_staking(
    address, snapshot
):  # TODO: Solve the duplication between LQTYV1 stakes and LQTY V2 stakes
    """
    Saves a snapshot of the total LQTY v1 stakes of a given address.
    Args:
        address (str): The address to check.
    """
    print("update_lqty_staking")
    lqty_staking = get_lqty_stakes(address)
    if lqty_staking:
        # Save PoolBalance
        protocol = ProtocolNetwork.objects.get(
            protocol__name="Liquity V1", network__name="Ethereum"
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


def update_lqty_v2_staking(address, snapshot):
    """
    Saves the total LQTY V2 governance stakes of a given address.
    Args:
        address (str): The address to check.
    """
    print("update_lqty_staking_v2")

    proxy_contract = get_proxy_staking_contract(address)
    lqty_staking = get_lqty_stakes(proxy_contract)
    if lqty_staking:
        # Save PoolBalance
        protocol = ProtocolNetwork.objects.get(
            protocol__name="Liquity V1", network__name="Ethereum"
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


def update_lqty_stability_pool(address, snapshot):
    """
    Saves the LQTY V1 stability pool participation of a given address.
    Args:
        address (str): The address to check.
    """
    print("update_lqty_stability_pool_v1")
    protocol = ProtocolNetwork.objects.get(
        protocol__name="Liquity V1", network__name="Ethereum"
    )
    pool = Pool.objects.get(
        protocol_network=protocol,
        name="stability pool",
    )
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        contract = Contract(pool.address)
        deposits = contract.deposits(address)
        if not deposits.initialValue:
            return {}
        ETH_gains = contract.getDepositorETHGain(address)
        LQTY_gains = contract.getDepositorLQTYGain(address)

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


def update_lqty_stability_pool_v2(address, snapshot):
    """
    Saves a snapshot of the participation of a given address in the three LIQUITY V2 stabiity pools .
    Args:
        address (str): The address to check.
    """
    print("update_lqty_stability_pool_v2")
    protocol = ProtocolNetwork.objects.get(
        protocol__name="Liquity V2", network__name="Ethereum"
    )
    pools = Pool.objects.filter(
        protocol_network=protocol,
        name__contains="stability pool",
    )
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        for pool in pools:
            contract = Contract(pool.address)
            deposits = contract.deposits(address)
            print(deposits)
            if not deposits:
                continue
            coll_gains = contract.getDepositorCollGain(address)
            yield_gains = contract.getDepositorYieldGain(address)

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
            if pool.name == "stability pool WETH":
                token = Cryptocurrency.objects.get(symbol="WETH")
            elif pool.name == "stability pool wstETH":
                token = Cryptocurrency.objects.get(symbol="wstETH")
            else:
                token = Cryptocurrency.objects.get(symbol="rETH")

            save_pool_rewards(
                address,
                pool,
                token,
                coll_gains / 1e18,
                snapshot,
            )
