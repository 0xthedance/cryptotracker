import logging
from typing import Optional

from cryptotracker.models import (
    ErrorLog,
    ErrorTypes,
    SnapshotError,
    Snapshot,
    UserAddress,
    Protocol,
    Cryptocurrency,
)


def log_snapshot_error(
    snapshot: Snapshot,
    error_type: str,
    user_address: UserAddress,
    protocol: Optional[Protocol] = None,
    cryptocurrency: Optional[Cryptocurrency] = None,
) -> None:
    """
    Logs an error message associated with a user address into the ErrorLog model.
    Args:
        user_address (UserAddress): The UserAddress instance related to the error.
        error_type (str): The error message to log.
        cryptocurrency (Cryptocurrency, optional): The Cryptocurrency instance related to the error. Defaults to None.
    """
    try:
        ErrorType_instance, created = ErrorTypes.objects.get_or_create(
            error_type=error_type
        )
        if created:
            logging.info(f"Created new ErrorType: {error_type}")

        ErrorLog_instance, created = ErrorLog.objects.get_or_create(
            user_address=user_address, error_type=ErrorType_instance
        )
        if created:
            logging.info(
                f"Created new ErrorLog for {user_address.public_address} with error type {error_type}"
            )

        SnapshotError.objects.create(
            snapshot=snapshot,
            error_log=ErrorLog_instance,
            protocol=protocol,
            cryptocurrency=cryptocurrency,
        )
        logging.info(f"Logged error for {user_address.public_address}: {error_type}")
    except Exception as e:
        logging.error(f"Failed to log error for {user_address.public_address}: {e}")
