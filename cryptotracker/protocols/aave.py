from ape import Contract, networks
from cryptotracker.models import Pool, UserAddress, ProtocolNetwork, Snapshot
from cryptotracker.protocols.protocols import save_pool_snapshot


def update_aave_lending_pools(user_address: UserAddress, snapshot: Snapshot) -> None:
    """
    Save the AAVE V3 lending pool participation of a given user_address (acting as a supplier only).
    Args:
        user_address (UserAddress): The user_address to check.

    """
    print("Serching aave pools")
    protocols = ProtocolNetwork.objects.filter(protocol__name="Aave V3")
    pools = Pool.objects.filter(
        protocol_network__in=protocols,
        type__name="lending pool",
    )

    for pool in pools:

        network = pool.protocol_network.network

        with networks.parse_network_choice(network.url_rpc):
            contract = Contract(pool.contract_address)
            provider_address = contract.getPoolDataProvider()
            provider = Contract(provider_address)
            tokens = provider.getAllReservesTokens()
            for token in tokens:
                token_address = token[1]
                try:
                    aave_pool_data = provider.getUserReserveData(token_address, user_address.public_address)
                except Exception as e:
                    print(f"Error fetching data for {token_address}: {e}")
                    aave_pool_data = None

                if not aave_pool_data or aave_pool_data.currentATokenBalance == 0:
                    continue

                # Save PoolBalanceSnapshot

                save_pool_snapshot(
                    pool,
                    user_address,
                    token[0],
                    aave_pool_data.currentATokenBalance / 1e18,
                    snapshot,
                )

