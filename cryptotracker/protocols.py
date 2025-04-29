from ape import Contract, networks

LQTY_GOVERN_CONTRACT = "0x636dEb767Cd7D0f15ca4aB8eA9a9b26E98B426AC"
LQTY_STAKING_CONTRACT = "0x4f9Fbb3f1E99B56e0Fe2892e623Ed36A76Fc605d"


def get_proxy_staking_contract(address: str)-> str:
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        lqty_govern_contract = Contract(LQTY_GOVERN_CONTRACT)
        return lqty_govern_contract.deriveUserProxyAddress(address)


def get_lqty_stakes(proxy_address):
    """
    Returns the LQTY governance stakes of a given address.
    Args:
        address (str): The address to check.
    Returns:
        list: A list of LQTY governance stakes.
    """
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        lqty_govern_contract = Contract(LQTY_STAKING_CONTRACT)
        lqty_govern_stakes = lqty_govern_contract.stakes(proxy_address)
        if not lqty_govern_stakes:
            return []
        
        

        


[ userStates(address) method Response ]
  unallocatedLQTY   uint256 :  0
  unallocatedOffset   uint256 :  0
  allocatedLQTY   uint256 :  100000000000000000000000
  allocatedOffset   uint256 :  173764317500000000000000000000000

        

    return LQTY_GOVERN_CONTRACT