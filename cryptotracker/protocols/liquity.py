from ape import Contract, networks
from cryptotracker.models import  Pool, Protocol, Cryptocurrency
from cryptotracker.protocols.protocols import save_pool_balance, save_pool_rewards


def get_proxy_staking_contract(address: str) -> str:
    protocol = Protocol.objects.get(name="Liquity V2", network__name="Ethereum")
    pool = Pool.objects.get(
        protocol=protocol,
        name="staking",
    )
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        lqty_govern_contract = Contract(pool.address)
        return lqty_govern_contract.deriveUserProxyAddress(address)

def get_lqty_stakes(address):

    """
    Returns the LQTY  stakes of a given address.
    Args:
        address (str): The address to check.
    Returns:
        list: A list of LQTY governance stakes.
    """
    protocol = Protocol.objects.get(name="Liquity V1", network__name="Ethereum")
    pool = Pool.objects.get(
        protocol=protocol,
        name ="staking",
    )
    print (pool)
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        contract = Contract(pool.address)
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

def update_lqty_v1_staking(address):
    """
    Saves the total LQTY v1 stakes of a given address.
    Args:
        address (str): The address to check.
    """
    lqty_staking = get_lqty_stakes(address)
    if lqty_staking:
        # Save PoolBalance
        pool = Pool.objects.get(
            protocol__name="Liquity V1",
            protocol__network__name="Ethereum",
            name="staking",
        )
        save_pool_balance(
            address,
            pool,
            Cryptocurrency.objects.get(name="LQTY"),
            lqty_staking["lqty_stakes"],
        )
        # Save PoolRewards
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(name="ETH"),
            lqty_staking["eth_rewards"],
        )
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(name="LUSD"),
            lqty_staking["lusd_rewards"],
        )

def update_lqty_v2_staking(address):
    """
    Saves the total LQTY governance stakes of a given address.
    Args:
        address (str): The address to check.
    """

    proxy_contract = get_proxy_staking_contract(address)
    lqty_staking = get_lqty_stakes(proxy_contract)
    if lqty_staking:
        # Save PoolBalance
        pool = Pool.objects.get(
            protocol__name="Liquity V2",
            protocol__network__name="Ethereum",
            name="staking",
        )
        save_pool_balance(
            address,
            pool,
            Cryptocurrency.objects.get(name="LQTY"),
            lqty_staking["lqty_stakes"],
        )
        # Save PoolRewards
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(name="ETH"),
            lqty_staking["eth_rewards"],
        )
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(name="LUSD"),
            lqty_staking["lusd_rewards"],
        )

def update_lqty_stability_pool(address):
    """
    Saves the LQTY V1 stability pool data of a given address.
    Args:
        address (str): The address to check.
    """
    protocol = Protocol.objects.get(name="Liquity V1", network__name="Ethereum")
    pool = Pool.objects.get(
        protocol=protocol,
        name="stability_pool",
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
            Cryptocurrency.objects.get(name="LUSD"),
            deposits.initialValue,
        )
        # Save PoolRewards
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(name="ETH"),
            ETH_gains,
        )
        save_pool_rewards(
            address,
            pool,
            Cryptocurrency.objects.get(name="LQTY"),
            LQTY_gains,
        )
    
def update_lqty_stability_pool_v2(address):
    """
    Returns the LQTY stability pool of a given address.
    Args:
        address (str): The address to check.
    Returns:
        dict: A dictionary containing the LQTY stability pool data.
    """
    protocol = Protocol.objects.get(name="Liquity V2", network__name="Ethereum")
    pools = Pool.objects.filter(
        protocol=protocol,
        name__contains="stability_pool",
    )
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        for pool in pools:
            contract = Contract(pool.address)
            deposits = contract.deposits(address)
            if not deposits:
                continue
            coll_gains = contract.getDepositorCollGain(address)
            yield_gains = contract.getDepositorYieldGain(address)

            # Save PoolBalance
            save_pool_balance(
                address,
                pool,
                Cryptocurrency.objects.get(name="BOLD"),
                deposits.initialValue,
            )

            #Save PoolRewards gains (BOLD) and collatera (WETH, wstETH and rETH )
            save_pool_rewards(
                address,
                pool,
                Cryptocurrency.objects.get(name="BOLD"),
                yield_gains,
            )
            if pool.name == "stability_pool_weth":
                token = Cryptocurrency.objects.get(name="WETH")
            elif pool.name == "stability_pool_wsteth":
                token = Cryptocurrency.objects.get(name="wstETH")
            elif pool.name == "stability_pool_reth":
                token = Cryptocurrency.objects.get(name="rETH")
            save_pool_rewards(
                address,
                pool,
                token,
                coll_gains,
            )