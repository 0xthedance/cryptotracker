from decimal import Decimal

from cryptotracker.utils import APIquery, fetch_historical_price

BEACONCHAN_API = "https://beaconcha.in/api/v1/validator"


class ValidatorDetails:
    """
    A class to represent validator details.
    """

    def __init__(
        self,
        index: int,
        public_key: str,
        withdrawal_credentials: str,
        balance: int,
        status: str,
        activation_epoch: int,
    ):
        self.index = index
        self.balance = balance
        self.status = status
        self.activation_epoch = activation_epoch
        self.public_key = public_key
        self.withdrawal_credentials = withdrawal_credentials

    def __repr__(self):
        return f"ValidatorDetails(index={self.index}, public_key={self.public_key}, withdrawal_credentials={self.withdrawal_credentials}, balance={self.balance}, status={self.status}, activation_epoch={self.activation_epoch})"


def get_aggregated_staking(accounts: list) -> dict:
    """
    Get the aggregated staking information for a list of accounts.
    Args:
        accounts (list): A list of Account objects.
    Returns:
        dict: A dictionary containing the aggregated staking information.
    """
    total_eth_staking = {}
    num_validators = 0
    balance = int(0)
    for account in accounts:
        validators = get_validators_from_withdrawal(account.public_address)
        print(f"Validators for {account.public_address}: {validators}")
        if validators == []:
            continue
        validator_details = get_validators_info(validators)
        num_validators += len(validator_details)
        print(num_validators)
        for validator in validator_details:
            balance += validator.balance
    current_price = fetch_historical_price("ethereum")[-1]["price"]
    balance_eur = (balance / 10e8) * current_price
    total_eth_staking = {
        "num_validators": num_validators,
        "balance": f"{balance / 10e8 :,.2f} ETH",
        "balance_eur": f"{balance_eur :,.2f} EUR",
    }
    return total_eth_staking


def get_validators_from_withdrawal(address: str) -> list[int]:
    """
    Get the validator indexs from the withdrawal credentials using Beaconcha API.
    Args:
        address (str): The withdrawal credentials address.
    Returns:
        list: A list of validator indexs.
    """
    validators = []
    params = {"limit": 10, "offset": 0}

    url = f"{BEACONCHAN_API}/withdrawalCredentials/{address}"
    # Fetch validator data from the API
    data = APIquery(url, params=params)
    if data is None:
        return []

    for validator in data["data"]:
        validator_index = validator["validatorindex"]
        validators.append(validator_index)

    return validators


def get_validators_info(validator_indexs: list[str]) -> list[ValidatorDetails]:
    """
    Get the validator details from the Beaconcha API.
    Args:
        validator_indexs (list): A list of validator indexs.
    Returns:
        list: A list of ValidatorDetails objects.
    """

    validator_details_list = []
    validator_indexs = [str(index) for index in validator_indexs]
    # Join the validator indexs into a comma-separated string
    validator_indexs = ",".join(validator_indexs)
    url = f"{BEACONCHAN_API}/{validator_indexs}"
    params = {}

    data = APIquery(url, params)
    if data is None:
        return []

    if isinstance(data["data"], dict):
        data["data"] = [data["data"]]

    for validator in data["data"]:
        if validator["status"] == "exited":
            continue

        index = validator["validatorindex"]
        public_key = validator["pubkey"]
        withdrawal_credentials = validator["withdrawalcredentials"]
        balance = validator["balance"]
        activation_epoch = validator["activationepoch"]
        status = validator["status"]

        validator_details = ValidatorDetails(
            index, public_key, withdrawal_credentials, balance, status, activation_epoch
        )
        validator_details_list.append(validator_details)

    return validator_details_list


def get_rewards(validator_indexs: list[int]) -> list[Decimal]:
    """
    Get the rewards for a list of validator indexs fetching
    execution and consensus rewards from BEACONCHA API.
    Args:
        validator_indexs (list): A list of validator indexs.
    Returns:
        list: A list of rewards for each validator.
    """
    rewards = {}
    validator_indexs = [str(index) for index in validator_indexs]
    validator_indexs = ",".join(validator_indexs)
    # Fetch rewards data from the API
    # Get the current execution reward performance
    url = f"{BEACONCHAN_API}/{validator_indexs}/execution/performance"
    data = APIquery(url, {})
    if data is not None:
        for validator in data["data"]:
            index = str(validator["validatorindex"])
            # Initialize the rewards dictionary for the validator
            if index not in rewards:
                rewards[index] = {}
            rewards[index]["executionperformance"] = Decimal(
                validator["performanceTotal"]
            )

    # Get the current consensus reward performance
    url = f"{BEACONCHAN_API}/{validator_indexs}/performance"
    data = APIquery(url, {})
    if data is not None:
        for validator in data["data"]:
            index = str(validator["validatorindex"])
            rewards[index]["consensusperformance"] = Decimal(
                validator["performancetotal"]
            )
            rewards[index]["performance"] = (
                rewards[index]["executionperformance"]
                + rewards[index]["consensusperformance"]
            )
    return rewards
