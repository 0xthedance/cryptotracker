from cryptotracker.models import Address, Snapshot, Cryptocurrency, Pool

from cryptotracker.protocols.subgraph import send_graphql_query
from cryptotracker.protocols.protocols import save_pool_balance, save_pool_rewards


UNISWAP_V3_SUBGRAPH_ID= "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"

PROTOCOL = "Uniswap V3"

NETWORK = "Ethereum"

POOL = "lending pool"


def update_uniswap_v3_positions(address: Address, snapshot: Snapshot) -> None:
    """Query all the troves for a given address using The Graph API and save snapshots"""
    print("Quering Uniswap v3 subgraph")
    pool = Pool.objects.get(
        name=POOL,
        protocol_network__protocol__name=PROTOCOL,
        protocol_network__network__name=NETWORK,
    )

    query = f"""
    {{
        positions(
            where: {{
                owner: "{address.public_address}",
                liquidity_gt: "0"}}

        ) {{
            id
            liquidity
            token0 {{
                symbol
                decimals
            }}
            token1 {{
                decimals
                symbol
            }}
        collectedFeesToken0
        collectedFeesToken1
        depositedToken0
        depositedToken1
        }}
    }}
    """

    response = send_graphql_query(UNISWAP_V3_SUBGRAPH_ID, query)

    if not response or "data" not in response or "positions" not in response["data"]:
        return None

    positions = response["data"]["positions"]

    print(positions)

    for position in positions:
        for key in [0,1]:
            token=Cryptocurrency.objects.get(symbol=position[f"token{key}"]["symbol"])
            if position[f"depositedToken{key}"] != "0":
                save_pool_balance(
                    address=address,
                    pool=pool,
                    token=token,
                    quantity=position[f"depositedToken{key}"],
                    snapshot=snapshot,
                )
            if position[f"collectedFeesToken{key}"] != "0":
                save_pool_rewards(
                    address=address,
                    pool=pool,
                    token=token,
                    quantity=position[f"collectedFeesToken{key}"],
                    snapshot=snapshot
                )
