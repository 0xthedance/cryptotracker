from cryptotracker.models import UserAddress, Snapshot, Cryptocurrency, Pool

from cryptotracker.protocols.subgraph import send_graphql_query
from cryptotracker.protocols.protocols import save_pool_snapshot
from cryptotracker.constants import POOL_TYPES, PROTOCOLS,NETWORKS



UNISWAP_V3_SUBGRAPH_ID= "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"



def update_uniswap_v3_positions(user_address: UserAddress, snapshot: Snapshot) -> None:
    """Query all the troves for a given user_address using The Graph API and save snapshots"""
    print("Quering Uniswap v3 subgraph")

    AAVE_LENDING_POOL = Pool.objects.get(
            type__name=POOL_TYPES["LENDING"],
            protocol_network__protocol__name=PROTOCOLS["AAVE"],
            protocol_network__network__name=NETWORKS["ETHEREUM"],
        )

    query = f"""
    {{
        positions(
            where: {{
                owner: "{user_address.public_address}",
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
                save_pool_snapshot(
                    pool=AAVE_LENDING_POOL,
                    address=user_address,
                    token_symbol=token,
                    quantity=position[f"depositedToken{key}"],
                    snapshot=snapshot,
                    pool_id = position["id"]
                )
            if position[f"collectedFeesToken{key}"] != "0":
                save_pool_snapshot(
                    pool=AAVE_LENDING_POOL,
                    address=user_address,
                    token_symbol=token,
                    quantity=position[f"collectedFeesToken{key}"],
                    snapshot=snapshot,
                    is_reward=True,
                    pool_id= position["id"]
                )
