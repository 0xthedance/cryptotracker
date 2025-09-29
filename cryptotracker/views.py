from decimal import Decimal
import logging
from typing import Any, List, Type, cast, Optional
from datetime import datetime


from celery.result import GroupResult
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from web3 import Web3

from cryptotracker.form import AccountForm, UserAddressForm, Dateform
from cryptotracker.models import Account, Snapshot, UserAddress, SnapshotError
from cryptotracker.protocols.protocols import get_protocols_snapshots
from cryptotracker.eth_staking import get_aggregated_staking, get_last_validators
from cryptotracker.tasks import run_daily_snapshot_update
from cryptotracker.tokens import fetch_aggregated_assets
from cryptotracker.constants import WALLET_TYPES
from cryptotracker.utils import get_last_price

# Create your views here.


def calculate_total_value(
    user_addresses: List[UserAddress],
    snapshot: Optional[Snapshot] = None,
) -> Decimal:
    """
    Helper function to calculate the total value for a given set of user_addresses.
    """
    if not snapshot:
        snapshot = Snapshot.objects.first()
        if not snapshot:
            logging.warning("No snapshot available for calculating total value.")
            return Decimal(0)
    aggregated_assets = fetch_aggregated_assets(user_addresses, snapshot=snapshot)
    total_eth_staking = get_aggregated_staking(user_addresses, snapshot=snapshot)
    total_protocols = get_protocols_snapshots(user_addresses, snapshot=snapshot)

    total_value = Decimal(0)
    for asset in aggregated_assets.values():
        total_value += asset["amount_eur"]
    if total_eth_staking:
        total_value += total_eth_staking["balance_eur"]
    if total_protocols:
        for protocol_pools in total_protocols["pool_data"].values():
            total_value += sum(data.balance_eur for data in protocol_pools)
        if total_protocols["troves"]:
            for trove in total_protocols["troves"]:
                total_value += trove.balance
    return total_value


def sign_up(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form: UserCreationForm = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("portfolio"))
    else:
        form = UserCreationForm()
    return render(request, "registration/sign_up.html", {"form": form})


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


@login_required()
def portfolio(request: HttpRequest, date_str: Optional[str] = None) -> HttpResponse:
    user = cast(User, request.user)

    error_warning = None
    date = None
    user_addresses = list(UserAddress.objects.filter(user=user))
    snapshot = None
    last_snapshot = Snapshot.objects.first()
    last_snapshot_date = last_snapshot.date if last_snapshot else None

    if date_str:
        # If a date is provided, filter the snapshots by that date
        date = datetime.strptime(date_str, "%Y-%m-%d")
        last_snapshot_date = date
        snapshot = Snapshot.objects.filter(date__date=date).first()
        if not snapshot:
            # If no snapshot exists for the given date, use the most recent one
            error_warning = "No snapshot found for the given date. Using the most recent snapshot instead."
            snapshot = None
            last_snapshot = Snapshot.objects.first()
            last_snapshot_date = last_snapshot.date if last_snapshot else None

    if request.method == "POST":
        form = Dateform(request.POST)
        if form.is_valid():
            date_str = form.clean_date()
            return redirect("portfolio_with_date", date_str=date_str)
    else:
        form = Dateform(initial={"date": date})

    aggregated_assets = fetch_aggregated_assets(user_addresses, snapshot=snapshot)
    total_eth_staking = get_aggregated_staking(user_addresses, snapshot=snapshot)
    total_protocols = get_protocols_snapshots(user_addresses, snapshot=snapshot)
    portfolio_value = calculate_total_value(user_addresses, snapshot=snapshot)
    error_logs = (
        SnapshotError.objects.filter(snapshot=last_snapshot) if last_snapshot else []
    )

    context = {
        "form3": form,
        "user": request.user,
        "assets": aggregated_assets,
        "staking": total_eth_staking,
        "protocols": total_protocols["pool_data"],
        "troves": total_protocols["troves"],
        "user_addresses": user_addresses,
        "portfolio_value": f"{portfolio_value:,.2f}",
        "last_snapshot": last_snapshot_date,
        "error_warning": error_warning,
        "errors": error_logs,
    }

    return render(request, "portfolio.html", context)


@login_required()
def staking(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)

    user_addresses = list(UserAddress.objects.filter(user=user))
    snapshot = Snapshot.objects.first()
    if snapshot:
        validators = get_last_validators(user_addresses, snapshot=snapshot)
    else:
        validators = []

    context = {
        "validators": validators,
    }
    return render(request, "staking.html", context)


@login_required()
def accounts(request: HttpRequest) -> HttpResponse:
    accounts_detail = []
    user = cast(User, request.user)
    accounts = list(Account.objects.filter(user=user))

    if accounts:
        for account in accounts:
            user_addresses = list(UserAddress.objects.filter(account=account))
            account_value = calculate_total_value(user_addresses)
            account_detail = {
                "account": account,
                "balance": f"{account_value:,.2f}",
            }
            accounts_detail.append(account_detail)

    if request.method == "POST":
        form = AccountForm(request.POST, user=user)
        if form.is_valid():
            account_name = form.clean_name()
            account = Account(
                user=user,
                name=account_name,
            )
            account.save()
            return redirect("accounts")
    else:
        form = AccountForm(user=request.user)

    context = {
        "accounts_detail": accounts_detail,
        "form3": form,
    }
    return render(request, "accounts.html", context)


@login_required
def delete_object(
    request: HttpRequest, model: Any, id: int, redirect_url: str, object_type: str
) -> HttpResponse:
    obj: Any = get_object_or_404(model, pk=id)

    if request.method == "POST":
        obj.delete()
        return redirect(redirect_url)

    # Render the confirmation page
    context = {
        "object_type": object_type,
        "redirect_url": redirect_url,
    }
    return render(request, "confirm_delete.html", context)


@login_required()
def user_addresses(request: HttpRequest) -> HttpResponse:
    addresses_detail = []
    user = cast(User, request.user)  # Ensure user is cast to User explicitly
    user_addresses = list(UserAddress.objects.filter(user=user))
    for user_address in user_addresses:
        address_value = calculate_total_value([user_address])

        address_detail = {
            "user_address": user_address,
            "balance": f"{address_value:,.2f}",
        }
        addresses_detail.append(address_detail)

    if request.method == "POST":
        form = UserAddressForm(request.POST, user=user)
        if form.is_valid():
            public_address = form.clean_public_address()
            if Web3.is_checksum_address(public_address) is False:
                public_address = Web3.to_checksum_address(public_address)

            user_address = UserAddress(
                user=user,
                public_address=public_address,
                wallet_type=form.cleaned_data["wallet_type"],
                name=form.cleaned_data["name"],
                account=form.cleaned_data["account"],
            )
            user_address.save()
            return redirect("user_addresses")
        else:
            logging.error(f"Form errors: {form.errors}")
            return render(request, "user_addresses.html", {"form1": form})

    context = {
        "addresses_detail": addresses_detail,
        "form1": UserAddressForm(user=user),
    }
    return render(request, "user_addresses.html", context)


@login_required()
def address_detail(request: HttpRequest, public_address: str) -> HttpResponse:
    user_address = UserAddress.objects.get(public_address=public_address)
    user_addresses = [user_address]

    aggregated_assets = fetch_aggregated_assets(user_addresses)
    total_eth_staking = get_aggregated_staking(user_addresses)
    total_protocols = get_protocols_snapshots(user_addresses)
    portfolio_value = calculate_total_value(user_addresses)

    last_snapshot = Snapshot.objects.first()
    last_snapshot_date = last_snapshot.date if last_snapshot else None
    errors = (
        SnapshotError.objects.filter(
            snapshot=last_snapshot, error_log__user_address=user_address
        )
        if last_snapshot
        else []
    )
    context = {
        "user": request.user,
        "assets": aggregated_assets,
        "staking": total_eth_staking,
        "protocols": total_protocols["pool_data"],
        "troves": total_protocols["troves"],
        "user_addresses": user_addresses,
        "portfolio_value": f"{portfolio_value:,.2f}",
        "last_snapshot": last_snapshot_date,
        "user_address": user_address,
        "errors": errors,
    }
    return render(request, "user_address_detail.html", context)


@login_required()
def rewards(request: HttpRequest) -> HttpResponse:
    """
    Show rewards for the portafolio, include staking rewards and protocol rewards.
    """
    user = cast(User, request.user)

    user_addresses = list(UserAddress.objects.filter(user=user))

    snapshot = Snapshot.objects.first()

    # Get ETH Staking rewards
    eth_rewards = Decimal(0)
    if snapshot:
        validators = get_last_validators(user_addresses, snapshot=snapshot)

        if validators:
            for validator in validators:
                current_price = get_last_price(
                    "ethereum", snapshot=validator.snapshot.date
                )
                eth_rewards += validator.rewards * current_price

    # Get protocol rewards
    rewards = {
        "ETH": f"{eth_rewards:,.2f}",
    }

    context = {
        "rewards": rewards,
        "total_rewards": f"{eth_rewards:,.2f}",
    }
    return render(request, "rewards.html", context)


@login_required()
def edit_object(
    request: HttpRequest,
    model: Any,
    id: int,
    form: Type,
    redirect_url: str,
    object_type: str,
) -> HttpResponse:
    obj = get_object_or_404(model, pk=id)

    if request.method == "POST":
        form_instance = form(request.POST, instance=obj)
        if form_instance.is_valid():
            form_instance.save()
            return redirect(redirect_url)
    else:
        form_instance = form(instance=obj)

    context = {
        "form2": form_instance,
        "object": obj,
        "object_type": object_type,
    }
    return render(request, "edit_object.html", context)


def logout_view(request: HttpRequest) -> None:
    logout(request)


@login_required()
def refresh(request: HttpRequest) -> HttpResponse:
    """
    Trigger the tasks asynchronously with a shared Snapshot.
    """

    task_group_result = run_daily_snapshot_update()

    request.session["task_group_id"] = task_group_result.id

    task_group_result.save()

    return redirect(reverse("waiting_page"))


@login_required()
def waiting_page(request: HttpRequest) -> HttpResponse:
    """
    Render the waiting page and check task status.
    """
    task_group_id = request.session.get("task_group_id")
    logging.info(f"Task group ID: {task_group_id}")

    if not task_group_id:
        return redirect(reverse("portfolio"))

    return render(request, "waiting_page.html", {"task_group_id": task_group_id})


@login_required()
def check_task_status(request: HttpRequest) -> JsonResponse:
    """
    Check the status of the task group and return a JSON response.
    """
    task_group_id = request.session.get("task_group_id")
    if not task_group_id:
        return JsonResponse({"status": "complete"})

    logging.info(f"Checking task group ID: {task_group_id}")

    task_group_result = GroupResult.restore(task_group_id)

    logging.info(task_group_result)

    if task_group_result and task_group_result.ready():
        # All tasks are complete
        return JsonResponse({"status": "complete"})

    return JsonResponse({"status": "pending"})


@login_required()
def statistics(request: HttpRequest) -> HttpResponse:
    """
    Show some statistics of the portfolio.
    """
    user = cast(User, request.user)
    user_addresses = list(UserAddress.objects.filter(user=user))

    wallet_values = {
        wallet: calculate_total_value(
            list(filter(lambda addr: addr.wallet_type.name == wallet, user_addresses))
        )
        for wallet in WALLET_TYPES.values()
    }

    # Amount (EUR) per account
    accounts_detail = []
    accounts = list(Account.objects.filter(user=user))
    for account in accounts:
        account_addresses = list(UserAddress.objects.filter(account=account))
        account_value = calculate_total_value(account_addresses)
        accounts_detail.append(
            {
                "account": account,
                "balance": account_value,
            }
        )

    context = {
        "hot_wallets_value": wallet_values[WALLET_TYPES["HOT"]],
        "cold_wallets_value": wallet_values[WALLET_TYPES["COLD"]],
        "smart_wallets_value": wallet_values[WALLET_TYPES["SMART"]],
        "accounts_detail": accounts_detail,
    }
    return render(request, "statistics.html", context)
