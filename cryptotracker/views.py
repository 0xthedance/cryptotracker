from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib.auth.models import User
from typing import List, cast, Type, Any

from web3 import Web3

from decimal import Decimal

from celery import group
from celery.result import GroupResult

from cryptotracker.form import AddressForm, AccountForm
from cryptotracker.models import Snapshot, Address, Account
from cryptotracker.staking import (
    get_aggregated_staking,
    get_last_validators,
)

from cryptotracker.tokens import (
    fetch_aggregated_assets,
)
from cryptotracker.tasks import (
    create_snapshot,
    update_assets_database,
    update_staking_assets,
    update_cryptocurrency_price,
    update_protocols,
)
from cryptotracker.utils import get_last_price

from cryptotracker.protocols.protocols import get_protocols_snapshots


# Create your views here.


def calculate_total_value(
    addresses: List[Address],
) -> Decimal:
    """
    Helper function to calculate the total value for a given set of addresses.
    """

    aggregated_assets = fetch_aggregated_assets(addresses)
    total_eth_staking = get_aggregated_staking(addresses)
    total_liquity_v1 = get_protocols_snapshots(addresses, protocol_name="Liquity V1")
    total_liquity_v2 = get_protocols_snapshots(addresses, protocol_name="Liquity V2")
    total_aave = get_protocols_snapshots(addresses, protocol_name="Aave V3")

    total_value = Decimal(0)
    for asset in aggregated_assets.values():
        total_value += asset["amount_eur"]
    if total_eth_staking:
        total_value += total_eth_staking["balance_eur"]
    if total_liquity_v1:
        for pool in total_liquity_v1.values():
            if pool == "borrow":
                for trove in pool["troves"]:
                    total_value += (trove.collateral - trove.debt)
                    continue
            for asset in pool["balances"].values():
                total_value += asset["balance_eur"]
    if total_liquity_v2:
        for pool in total_liquity_v2.values():
            if pool == "borrow":
                for trove in pool["troves"]:
                    total_value += (trove.collateral - trove.debt)
                    continue
            for asset in pool["balances"].values():
                total_value += asset["balance_eur"]
    if total_aave:
        for pool in total_aave.values():
            for asset in pool["balances"].values():
                total_value += asset["balance_eur"]
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
def portfolio(request: HttpRequest) -> HttpResponse:
    
    user = cast(User, request.user)

    addresses = list(Address.objects.filter(user=user))   
    last_snapshot = Snapshot.objects.first()
    aggregated_assets = fetch_aggregated_assets(addresses)
    total_eth_staking = get_aggregated_staking(addresses)
    total_liquity_v1 = get_protocols_snapshots(addresses, protocol_name="Liquity V1")
    total_liquity_v2 = get_protocols_snapshots(addresses, protocol_name="Liquity V2")
    total_aave = get_protocols_snapshots(addresses, protocol_name="Aave V3")
    portfolio_value = calculate_total_value(addresses)

    if last_snapshot:
        last_snapshot_date = last_snapshot.date  # Use a separate variable for datetime
    else:
        last_snapshot_date = None
    context = {
        "user": request.user,
        "assets": aggregated_assets,
        "staking": total_eth_staking,
        "protocols": {
            "Liquity V1": total_liquity_v1,
            "Liquity V2": total_liquity_v2,
            "Aave V3": total_aave,
        },
        "addresses": addresses,
        "portfolio_value": f"{portfolio_value:,.2f}",
        "last_snapshot": last_snapshot_date,
    }

    return render(request, "portfolio.html", context)


@login_required()
def staking(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)

    addresses = list(Address.objects.filter(user=user))   
    validators = get_last_validators(addresses)

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
            addresses = list(Address.objects.filter(account=account))  
            account_value = calculate_total_value(addresses)
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
    request: HttpRequest, 
    model: Any,  
    id: int, 
    redirect_url: str, 
    object_type: str
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
def addresses(request: HttpRequest) -> HttpResponse:
    addresses_detail = []
    user = cast(User, request.user)  # Ensure user is cast to User explicitly
    addresses = list(Address.objects.filter(user=user))  # Correct type for lookup
    for address in addresses:
        address_value = calculate_total_value([address])  # Wrap single address in a list
        address_detail = {
            "address": address,
            "balance": f"{address_value:,.2f}",
        }
        addresses_detail.append(address_detail)

    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            public_address = form.clean_public_address()
            if Web3.is_checksum_address(public_address) is False:
                public_address = Web3.to_checksum_address(public_address)

            address = Address(
                user=user,
                public_address=public_address,
                wallet_type=form.cleaned_data["wallet_type"],
                name=form.cleaned_data["name"],
                account=form.cleaned_data["account"],
            )
            address.save()
            return redirect("addresses")

    context = {
        "addresses_detail": addresses_detail,
        "form1": AddressForm(),
    }
    return render(request, "addresses.html", context)


@login_required()
def address_detail(request: HttpRequest, public_address: str) -> HttpResponse:
    address = Address.objects.get(public_address=public_address)
    addresses = [address]
    aggregated_assets = fetch_aggregated_assets(addresses)
    total_eth_staking = get_aggregated_staking(addresses)
    total_liquity_v1 = get_protocols_snapshots(addresses, protocol_name="Liquity V1")
    total_liquity_v2 = get_protocols_snapshots(addresses, protocol_name="Liquity V2")
    total_aave = get_protocols_snapshots(addresses, protocol_name="Aave V3")
    portfolio_value = calculate_total_value(addresses)

    last_snapshot = Snapshot.objects.first()
    last_snapshot_date = last_snapshot.date if last_snapshot else None  # Fix type mismatch
    context = {
        "user": request.user,
        "assets": aggregated_assets,
        "staking": total_eth_staking,
        "protocols": {
            "Liquity V1": total_liquity_v1,
            "Liquity V2": total_liquity_v2,
            "Aave V3": total_aave,
        },
        "addresses": addresses,
        "portfolio_value": f"{portfolio_value:,.2f}",
        "last_snapshot": last_snapshot_date,
        "address": address,
    }
    return render(request, "address_detail.html", context)


@login_required()
def rewards(request: HttpRequest) -> HttpResponse:
    """
    Show rewards for the portafolio, include staking rewards and protocol rewards.
    """
    user = cast(User, request.user)  

    addresses = list(Address.objects.filter(user=user))   

    # Get ETH Staking rewards
    eth_rewards = Decimal(0)  # Ensure proper type for rewards
    validators = get_last_validators(addresses)

    if validators:

        for validator in validators:
            current_price = get_last_price("ethereum", snapshot=validator.snapshot.date)
            eth_rewards += validator.rewards * current_price

    # Get protocol rewards

    rewards = {
        "ETH": f"{eth_rewards:,.2f}",
    }

    total_rewards = eth_rewards
    context = {
        "rewards": rewards,
        "total_rewards": f"{total_rewards:,.2f}",
    }
    return render(request, "rewards.html", context)


@login_required()
def edit_object(
    request: HttpRequest, 
    model: Any, 
    id: int, 
    form: Type,  
    redirect_url: str, 
    object_type: str
) -> HttpResponse:
    
    obj= get_object_or_404(model, pk=id)  

    if request.method == "POST":
        form_instance = form(request.POST, instance=obj) 
        if form_instance.is_valid():
            form_instance.save() 
            return redirect(redirect_url)
    else:
        form_instance = form(instance=obj) 

    # Render the edit page
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
    # Create a Snapshot and get its ID
    snapshot_id = create_snapshot()

    # Trigger the tasks asynchronously
    task_group = group(
        update_cryptocurrency_price.s(snapshot_id),
        update_assets_database.s(snapshot_id),
        update_staking_assets.s(snapshot_id),
        update_protocols.s(snapshot_id),
    )

    # Execute the task group asynchronously
    task_group_result = task_group.apply_async()
    print(f"Task group ID: {task_group_result.id}")

    request.session["task_group_id"] = task_group_result.id

    task_group_result.save()

    return redirect(reverse("waiting_page"))


@login_required()
def waiting_page(request: HttpRequest) -> HttpResponse:
    """
    Render the waiting page and check task status.
    """
    task_group_id = request.session.get("task_group_id")
    print(f"Task group ID: {task_group_id}")
    if not task_group_id:
        return redirect(reverse("portfolio"))

    # Render the waiting page
    return render(request, "waiting_page.html", {"task_group_id": task_group_id})


@login_required()
def check_task_status(request: HttpRequest) -> JsonResponse:
    """
    Check the status of the task group and return a JSON response.
    """
    task_group_id = request.session.get("task_group_id")
    if not task_group_id:
        return JsonResponse({"status": "complete"})

    print(f"Checking task group ID: {task_group_id}")

    task_group_result = GroupResult.restore(task_group_id)

    print(task_group_result)

    if task_group_result and task_group_result.ready():
        # All tasks are complete
        return JsonResponse({"status": "complete"})

    # Tasks are still running
    return JsonResponse({"status": "pending"})


@login_required()
def statistics(request: HttpRequest) -> HttpResponse:
    """
    Show some statistics of the portfolio.
    """
    user = cast(User, request.user)  # Ensure user is cast to User explicitly
    addresses = list(Address.objects.filter(user=user))  # Correct type for lookup

    # Statistic balance per type of wallet

    wallet_types = ["HOT", "COLD", "SMART"]

    wallet_values = {
        wallet: calculate_total_value(
            list(filter(lambda addr: addr.wallet_type.name == wallet, addresses))  # Fix filter logic
        )
        for wallet in wallet_types
    }

    # Amount (EUR) per account
    accounts_detail = []
    accounts = list(Account.objects.filter(user=user))  
    for account in accounts:
        account_addresses = list(Address.objects.filter(account=account))  
        account_value = calculate_total_value(account_addresses)
        accounts_detail.append(
            {
                "account": account,
                "balance": account_value,
            }
        )

    context = {
        "hot_wallets_value": wallet_values["HOT"],
        "cold_wallets_value": wallet_values["COLD"],
        "smart_wallets_value": wallet_values["SMART"],
        "accounts_detail": accounts_detail,
    }
    return render(request, "statistics.html", context)
