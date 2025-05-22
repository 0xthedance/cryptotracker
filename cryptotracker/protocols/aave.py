from ape import Contract, networks
from cryptotracker.models import Pool, Cryptocurrency, Network
from cryptotracker.protocols.protocols import save_pool_balance


def update_aave_lending_pools(address: str) -> dict:
    """
    Save the AAVE V3 lending pool of a given address acting as a supplier.
    Args:
        address (str): The address to check.

    """

    for network in Network.objects.all():

        pool = Pool.objects.get(
            protocol__name="Aave V3",
            protocol__network=network,
            name="lending_pool",
        )

        with networks.parse_network_choice(network.url_rpc):
            contract = Contract(pool.address)
            provider_address = contract.getPoolDataProvider()
            provider = Contract(provider_address)
            tokens = provider.getAllReservesTokens()
            for token in tokens:
                token_address = token[1]
                try:
                    aave_pool_data = provider.getUserReserveData(token_address, address)
                except Exception as e:
                    print(f"Error fetching data for {token_address}: {e}")
                    aave_pool_data = None
                if not aave_pool_data or aave_pool_data.currentATokenBalance == 0:
                    continue
                # Save PoolBalance
                save_pool_balance(
                    address,
                    pool,
                    Cryptocurrency.objects.get(symbol=token[0]),
                    aave_pool_data.currentATokenBalance / 1e18,
                )
