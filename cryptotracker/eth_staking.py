import os
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union

import backoff
import requests

from cryptotracker.models import Snapshot, UserAddress, Validator, ValidatorSnapshot
from cryptotracker.utils import get_last_price, log_backoff

BEACONCHAIN_API_URL_V2 = "https://beaconcha.in/api/v2/ethereum"
BEACONCHAIN_API_KEY = os.environ.get("BEACONCHAIN_API_KEY")

if not BEACONCHAIN_API_KEY:
    logging.warning(
        "BEACONCHAIN_API_KEY environment variable not set. beaconcha.in API calls will fail."
    )


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.RequestException, ValueError, KeyError),
    max_tries=3,
    max_time=180,
    on_backoff=log_backoff,
)
def beaconcha_v2_post(endpoint: str, payload: Dict) -> Optional[Dict]:
    url = f"{BEACONCHAIN_API_URL_V2}{endpoint}"
    headers = {
        "Authorization": f"Bearer {BEACONCHAIN_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
    except requests.exceptions.RequestException as e:
        logging.error(f"{url} request failed: {e}")
        return None
    if response.status_code != 200:
        logging.error(
            f"{url} request failed with HTTP status code {response.status_code} and text {response.text}"
        )
        return None
    return response.json()


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
    user_addresses: List[UserAddress], snapshot: Snapshot
) -> Optional[List[ValidatorSnapshot]]:
    """
    Get the last staking assets for a list of user_addresses.
    Args:
        user_addresses (list): A list of UserAddress objects.
    Returns:
        list: A list of ValidatorSnapshot objects or None if no validators exist.
    """
    last_validators = ValidatorSnapshot.objects.filter(
        validator__user_address__in=user_addresses, snapshot=snapshot
    )
    if not last_validators:
        return None
    return list(last_validators)


def get_aggregated_staking(
    user_addresses: List[UserAddress], snapshot: Optional[Snapshot] = None
) -> Optional[Dict[str, Union[int, Decimal]]]:
    """
    Get the aggregated staking information for a list of user_addresses.
    Args:
        user_addresses (list): A list of UserAddress objects.
    Returns:
        dict: A dictionary containing the aggregated staking information or None if no validators exist.
    """
    if snapshot is None:
        snapshot = Snapshot.objects.first()
        if not snapshot:
            return None
    total_eth_staking: Dict[str, Union[int, Decimal]] = {}
    num_validators = 0
    balance = Decimal(0)
    rewards = Decimal(0)
    last_validators = get_last_validators(user_addresses, snapshot)
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
    Get the validator indexes from the withdrawal credentials using Beaconcha API V2.
    Args:
        user_address (str): The withdrawal credentials user_address.
    Returns:
        list: A list of validator indexes.
    """
    validators: List[int] = []
    cursor = ""

    while True:
        payload = {
            "chain": "mainnet",
            "validator": {"withdrawal": user_address},
            "page_size": 10,
        }
        if cursor:
            payload["cursor"] = cursor

        data = beaconcha_v2_post("/validators", payload)
        if data is None:
            return validators

        for item in data["data"]:
            validators.append(item["validator"]["index"])

        next_cursor = data.get("paging", {}).get("next_cursor")
        if not next_cursor:
            break
        cursor = next_cursor

    return validators


def get_validators_info(validator_indexes: List[int]) -> List[ValidatorDetails]:
    """
    Get the validator details from the Beaconcha API V2.
    Args:
        validator_indexes (list): A list of validator indexes.
    Returns:
        list: A list of ValidatorDetails objects.
    """
    validator_details_list: List[ValidatorDetails] = []

    payload = {
        "chain": "mainnet",
        "validator": {"validator_identifiers": validator_indexes},
        "page_size": 10,
    }
    data = beaconcha_v2_post("/validators", payload)
    if data is None:
        return []

    for item in data["data"]:
        status = item["status"]
        if status.startswith("exited") or status.startswith("withdrawal"):
            continue

        index = item["validator"]["index"]
        public_key = item["validator"]["public_key"]
        withdrawal_credentials = item["withdrawal_credentials"]["credential"]
        balance = int(item["balances"]["current"]) / 1e18  # Convert wei to ETH
        activation_epoch = item["life_cycle_epochs"]["activation"]
        if activation_epoch is not None:
            activation_date = convert_epoch_datetime(activation_epoch)
        else:
            activation_date = ""

        validator_details = ValidatorDetails(
            index, public_key, withdrawal_credentials, balance, status, activation_date
        )
        validator_details_list.append(validator_details)

    return validator_details_list


def get_rewards(validator_indexes: List[int]) -> Dict[str, Dict[str, float]]:
    """
    Get the rewards for a list of validator indexes using
    the Beaconcha API V2 rewards-list endpoint.
    Args:
        validator_indexes (list): A list of validator indexes.
    Returns:
        dict: A dictionary containing rewards for each validator.
    """
    rewards: Dict[str, Dict[str, float]] = {}
    if not validator_indexes:
        return rewards

    for idx in validator_indexes:
        rewards[str(idx)] = {"performance": 0}

    state_data = beaconcha_v2_post("/state", {"chain": "mainnet"})
    if state_data is None:
        return rewards
    current_epoch = state_data.get("data", {}).get("current_epoch")
    if current_epoch is None:
        return rewards

    epoch = max(0, current_epoch - 1)

    payload = {
        "chain": "mainnet",
        "validator": {"validator_identifiers": validator_indexes},
        "epoch": epoch,
    }
    data = beaconcha_v2_post("/validators/rewards-list", payload)
    if data is not None:
        for item in data["data"]:
            index = str(item["validator"]["index"])
            total_wei = int(item["total"])
            rewards[index]["performance"] = total_wei / 1e18  # Convert wei to ETH

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
