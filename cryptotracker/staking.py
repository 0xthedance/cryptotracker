from decimal import Decimal


from cryptotracker.utils import APIquery, get_last_price
from cryptotracker.models import SnapshotETHValidator, SnapshotDate

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


def get_last_validators(addresses: list) -> list[SnapshotETHValidator]:
    """
    Get the last staking assets for a list of addresses.
    Args:
        addresses (list): A list of Address objects.
    Returns:
        list: A list of SnapshotETHValidator objects.
    """
    last_snapshot_date = SnapshotDate.objects.first()
    last_validators = SnapshotETHValidator.objects.filter(
        address__in=addresses, snapshot_date=last_snapshot_date
    )
    if not last_validators:
        return None
    return last_validators


def get_aggregated_staking(addresses: list) -> dict:
    """
    Get the aggregated staking information for a list of addresses.
    Args:
        addresses (list): A list of Address objects.
    Returns:
        dict: A dictionary containing the aggregated staking information.
    """
    total_eth_staking = {}
    num_validators = int(0)
    balance = int(0)
    rewards = int(0)
    last_validators = get_last_validators(addresses)
    if last_validators is None:
        return None
    num_validators = len(last_validators)
    for validator in last_validators:
        balance += validator.balance
        rewards += validator.rewards
    current_price = get_last_price("ethereum", last_validators[0].snapshot_date.date)
    balance_eur = balance * current_price
    total_eth_staking = {
        "num_validators": num_validators,
        "balance": balance,
        "balance_eur": balance_eur,
        "rewards": rewards,
    }
    return total_eth_staking


def fetch_staking_assets(address: str, snapshot_date):
    """
    Fetch the staking assets of a user from the Ethereum blockchain and store them in the database.
    This function uses the Ape library to interact with the Ethereum blockchain and fetch the balance of each token.
    It also fetches the current price of each token using the fetch_historical_price function from Coingeko app
    Args:
        address (str): The public address of the address.
    """
    validators = get_validators_from_withdrawal(address.public_address)

    if validators == []:
        return
    validator_details = get_validators_info(validators)
    rewards = get_rewards(validators)
    for validator in validator_details:
        # Save the validator details to the database

        validator_snapshot = SnapshotETHValidator(
            address=address,
            validator_index=validator.index,
            public_key=validator.public_key,
            balance=validator.balance,
            status=validator.status,
            activation_epoch=validator.activation_epoch,
            rewards=rewards[str(validator.index)]["performance"],
            snapshot_date=snapshot_date,
        )
        validator_snapshot.save()


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
        balance = validator["balance"] / 1e9  # Convert Gwei to Decimal
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
            rewards[index]["executionperformance"] = (
                validator["performanceTotal"] / 1e18
            )

    # Get the current consensus reward performance
    url = f"{BEACONCHAN_API}/{validator_indexs}/performance"
    data = APIquery(url, {})
    if data is not None:
        for validator in data["data"]:
            index = str(validator["validatorindex"])
            rewards[index]["consensusperformance"] = validator["performancetotal"] / 1e9
            rewards[index]["performance"] = (
                rewards[index]["executionperformance"]
                + rewards[index]["consensusperformance"]
            )
    return rewards
