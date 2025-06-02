from ape import Contract, networks
from cryptotracker.models import Pool, Cryptocurrency, Address, ProtocolNetwork, Snapshot
from cryptotracker.protocols.protocols import save_pool_balance


def update_aave_lending_pools(address: Address, snapshot: Snapshot) -> None:
    """
    Save the AAVE V3 lending pool participation of a given address (acting as a supplier only).
    Args:
        address (Address): The address to check.

    """
    print("Serching aave pools")
    protocols = ProtocolNetwork.objects.filter(protocol__name="Aave V3")
    pools = Pool.objects.filter(
        protocol_network__in=protocols,
        name="lending pool",
    )

    for pool in pools:

        network = pool.protocol_network.network
        print(network)

        with networks.parse_network_choice(network.url_rpc):
            contract = Contract(pool.address)
            provider_address = contract.getPoolDataProvider()
            provider = Contract(provider_address)
            tokens = provider.getAllReservesTokens()
            for token in tokens:
                token_address = token[1]
                try:
                    aave_pool_data = provider.getUserReserveData(token_address, address.public_address)
                except Exception as e:
                    print(f"Error fetching data for {token_address}: {e}")
                    aave_pool_data = None

                if not aave_pool_data or aave_pool_data.currentATokenBalance == 0:
                    continue
                # Save PoolBalance
                save_pool_balance(
                    address=address,
                    pool=pool,
                    token=Cryptocurrency.objects.get(symbol=token[0]),
                    quantity=aave_pool_data.currentATokenBalance / 1e18,
                    snapshot=snapshot,
                )
