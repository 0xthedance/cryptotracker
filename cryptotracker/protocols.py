from ape import Contract, networks
from cryptotracker.models import Network, Pool

# Liquity V2 contracts
LQTY_GOVERN_CONTRACT = "0x636dEb767Cd7D0f15ca4aB8eA9a9b26E98B426AC"

# Liquity V1 contracts
LQTY_STAKING_CONTRACT = "0x4f9Fbb3f1E99B56e0Fe2892e623Ed36A76Fc605d"


def get_proxy_staking_contract(address: str) -> str:
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        lqty_govern_contract = Contract(LQTY_GOVERN_CONTRACT)
        return lqty_govern_contract.deriveUserProxyAddress(address)


def get_lqty_staking(address):
    """
    Returns the LQTY governance stakes of a given address.
    Args:
        address (str): The address to check.
    Returns:
        list: A list of LQTY governance stakes.
    """
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        contract = Contract(LQTY_STAKING_CONTRACT)
        lqty_stakes = contract.stakes(address)
        if not lqty_stakes:
            return {}
        eth_rewards = contract.getPendingETHGain(address)
        lusd_rewards = contract.getPendingLUSDGain(address)
        lqty_staking = {
            "lqty_stakes": lqty_stakes,
            "eth_rewards": eth_rewards,
            "lusd_rewards": lusd_rewards,
        }
        return lqty_staking


def get_total_lqty_staking(address):
    """
    Returns the total LQTY governance stakes of a given address.
    Args:
        address (str): The address to check.
    Returns:
        dict: A dictionary containing the total LQTY governance stakes.
    """

    lqty_staking_v1 = get_lqty_staking(address)
    # Get LQTY staking v2 in governance contract

    proxy_contract = get_proxy_staking_contract(address)
    lqty_staking_v2 = get_lqty_staking(proxy_contract)


# AAVE V3 contracts
AAVE_LENDING_POOL = {
    "Ethereum": "",
    "Arbitrum": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb",
    "Avalanche": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb",
    "Gnosis Chain": "0x36616cf17557639614c1cdDb356b1B83fc0B2132",
    "Base": "0xe20fCBdBfFC4Dd138cE8b2E6FBb6CB49777ad64D",
}


def get_aave_lending_pool_data(address: str) -> dict:
    """
    Returns the AAVE V3 lending pool of a given address.
    Args:
        address (str): The address to check.
    Returns:
        dict: A dictionary containing the AAVE V3 lending pool data.
    """
    for network in Network.objects.all():

        pool = Pool.objects.filter(
            protocol__name="Aave V3",
            protocol__network=network,
            name="lending_pool",
        )

        provider = get_pool_data_provider(pool)

        with networks.parse_network_choice("network.url_rpc"):
            contract = Contract(pool.address)
            provider_address = contract.getPoolDataProvider()
            provider = Contract(provider_address)
            aave_pool_data = provider.getUserAccountData(address)

    return aave_pool_data
