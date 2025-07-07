from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union

from cryptotracker.models import Snapshot, UserAddress, Validator, ValidatorSnapshot
from cryptotracker.utils import APIquery, get_last_price

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
        balance: float,
        status: str,
        activation_date: str,
    ):
        self.index = index
        self.balance = balance
        self.status = status
        self.activation_date = activation_date
        self.public_key = public_key
        self.withdrawal_credentials = withdrawal_credentials

    def __repr__(self) -> str:
        return (
            f"ValidatorDetails(index={self.index}, public_key={self.public_key}, "
            f"withdrawal_credentials={self.withdrawal_credentials}, balance={self.balance}, "
            f"status={self.status}, activation_date={self.activation_date})"
        )


def get_last_validators(
    user_addresses: List[UserAddress],
) -> Optional[List[ValidatorSnapshot]]:
    """
    Get the last staking assets for a list of user_addresses.
    Args:
        user_addresses (list): A list of UserAddress objects.
    Returns:
        list: A list of ValidatorSnapshot objects or None if no validators exist.
    """
    last_snapshot = Snapshot.objects.first()
    last_validators = ValidatorSnapshot.objects.filter(
        validator__user_address__in=user_addresses, snapshot=last_snapshot
    )
    if not last_validators:
        return None
    return list(last_validators)


def get_aggregated_staking(
    user_addresses: List[UserAddress],
) -> Optional[Dict[str, Union[int, Decimal]]]:
    """
    Get the aggregated staking information for a list of user_addresses.
    Args:
        user_addresses (list): A list of UserAddress objects.
    Returns:
        dict: A dictionary containing the aggregated staking information or None if no validators exist.
    """
    total_eth_staking: Dict[str, Union[int, Decimal]] = {}
    num_validators = 0
    balance = Decimal(0)
    rewards = Decimal(0)
    last_validators = get_last_validators(user_addresses)
    if last_validators is None:
        return None
    num_validators = len(last_validators)
    for validator in last_validators:
        balance += validator.balance
        rewards += validator.rewards
    current_price = get_last_price("ethereum", last_validators[0].snapshot.date)
    balance_eur = balance * current_price
    total_eth_staking = {
        "num_validators": num_validators,
        "balance": balance,
        "balance_eur": balance_eur,
        "rewards": rewards,
    }
    return total_eth_staking


def fetch_staking_assets(user_address: UserAddress, snapshot: Snapshot) -> None:
    """
    Fetch the staking assets of a user from the Ethereum blockchain and store them in the database.
    Args:
        user_address (UserAddress): The UserAddress object.
        snapshot (Snapshot): The Snapshot object.
    """
    validators = get_validators_from_withdrawal(user_address.public_address)

    if not validators:
        return

    validator_details = get_validators_info(validators)
    rewards = get_rewards(validators)

    for validator in validator_details:
        # Create or get the Validator object
        validator_obj, _ = Validator.objects.get_or_create(
            user_address=user_address,
            validator_index=validator.index,
            defaults={
                "public_key": validator.public_key,
                "activation_date": validator.activation_date,
            },
        )
        print(f"Processing validator: {validator.index}")

        # Save the validator snapshot
        ValidatorSnapshot.objects.create(
            validator=validator_obj,
            balance=validator.balance,
            status=validator.status,
            rewards=rewards[str(validator.index)]["performance"],
            snapshot=snapshot,
        )


def get_validators_from_withdrawal(user_address: str) -> List[int]:
    """
    Get the validator indexes from the withdrawal credentials using Beaconcha API.
    Args:
        user_address (str): The withdrawal credentials user_address.
    Returns:
        list: A list of validator indexes.
    """
    validators: List[int] = []
    params = {"limit": 10, "offset": 0}

    url = f"{BEACONCHAN_API}/withdrawalCredentials/{user_address}"
    # Fetch validator data from the API
    data = APIquery(url, params=params)
    if data is None:
        return []

    for validator in data["data"]:
        validator_index = validator["validatorindex"]
        validators.append(validator_index)

    return validators


def get_validators_info(validator_indexes: List[int]) -> List[ValidatorDetails]:
    """
    Get the validator details from the Beaconcha API.
    Args:
        validator_indexes (list): A list of validator indexes.
    Returns:
        list: A list of ValidatorDetails objects.
    """
    validator_details_list: List[ValidatorDetails] = []
    validator_indexes_str = ",".join(map(str, validator_indexes))
    url = f"{BEACONCHAN_API}/{validator_indexes_str}"
    params: dict = {}

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
        activation_date = convert_epoch_datetime(validator["activationepoch"])
        status = validator["status"]

        validator_details = ValidatorDetails(
            index, public_key, withdrawal_credentials, balance, status, activation_date
        )
        validator_details_list.append(validator_details)

    return validator_details_list


def get_rewards(validator_indexes: List[int]) -> Dict[str, Dict[str, float]]:
    """
    Get the rewards for a list of validator indexes fetching
    execution and consensus rewards from BEACONCHA API.
    Args:
        validator_indexes (list): A list of validator indexes.
    Returns:
        dict: A dictionary containing rewards for each validator.
    """
    rewards: Dict[str, Dict[str, float]] = {}
    validator_indexes_str = ",".join(map(str, validator_indexes))
    # Fetch rewards data from the API
    # Get the current execution reward performance
    url = f"{BEACONCHAN_API}/{validator_indexes_str}/execution/performance"
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
    url = f"{BEACONCHAN_API}/{validator_indexes_str}/performance"
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


def convert_epoch_datetime(epoch: int) -> str:
    """
    Helper to convert epoch to datetime (assume 12 seconds per slot, 32 slots per epoch).
    Args:
        epoch (int): The epoch number.
    Returns:
        str: The activation date in YYYY-MM-DD format.
    """
    seconds_since_genesis = epoch * 32 * 12
    genesis_time = datetime(2020, 12, 1, 12, 0, 23)  # Beacon Chain genesis time
    activation_time = genesis_time.timestamp() + seconds_since_genesis

    return datetime.fromtimestamp(activation_time).strftime("%Y-%m-%d")
