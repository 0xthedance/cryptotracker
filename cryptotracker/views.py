from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse

from web3 import Web3

from celery import group
from celery.result import GroupResult

from cryptotracker.form import EditAddressForm, AddressForm, AccountForm
from cryptotracker.models import Snapshot, Price, Address, Account, ValidatorSnapshot
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
    addresses: list,
) -> float:
    """
    Helper function to calculate the total value for a given set of addresses.
    """

    aggregated_assets = fetch_aggregated_assets(addresses)
    total_eth_staking = get_aggregated_staking(addresses)
    total_liquity_v1 = get_protocols_snapshots(addresses, protocol_name="Liquity V1")
    total_liquity_v2 = get_protocols_snapshots(addresses, protocol_name="Liquity V2")
    total_aave = get_protocols_snapshots(addresses, protocol_name="Aave V3")

    total_value = 0
    for asset in aggregated_assets.values():
        total_value += asset["amount_eur"]
    if total_eth_staking:
        total_value += total_eth_staking["balance_eur"]
    if total_liquity_v1:
        for pools in total_liquity_v1.values():
            for asset in pools["balances"].values():
                total_value += asset["balance_eur"]
    if total_liquity_v2:
        for pools in total_liquity_v2.values():
            for asset in pools["balances"].values():
                total_value += asset["balance_eur"]
    if total_aave:
        for pools in total_aave.values():
            for asset in pools["balances"].values():
                total_value += asset["balance_eur"]
    return total_value


def sign_up(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("portfolio"))
    else:
        form = UserCreationForm()
    return render(request, "registration/sign_up.html", {"form": form})


def home(request):
    return render(request, "home.html")


@login_required()
def portfolio(request):
    addresses = Address.objects.filter(user=request.user)
    last_snapshot = Snapshot.objects.first()
    aggregated_assets = fetch_aggregated_assets(addresses)
    total_eth_staking = get_aggregated_staking(addresses)
    total_liquity_v1 = get_protocols_snapshots(addresses, protocol_name="Liquity V1")
    print(total_liquity_v1, "total LQUITY V1")
    total_liquity_v2 = get_protocols_snapshots(addresses, protocol_name="Liquity V2")
    print(total_liquity_v2, "total LQUITY V2")

    total_aave = get_protocols_snapshots(addresses, protocol_name="Aave V3")
    portfolio_value = calculate_total_value(addresses)

    if last_snapshot:
        last_snapshot = last_snapshot.date
    else:
        last_snapshot = None
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
        "last_snapshot": last_snapshot,
    }

    return render(request, "portfolio.html", context)


@login_required()
def staking(request):
    addresses = Address.objects.filter(user=request.user)
    validators = get_last_validators(addresses)

    context = {
        "validators": validators,
    }
    return render(request, "staking.html", context)


@login_required()
def accounts(request):
    accounts_detail = []
    accounts = Account.objects.filter(user=request.user)

    if accounts:
        for account in accounts:
            accounts = [account]
            addresses = Address.objects.filter(account=account)

            account_value = calculate_total_value(addresses)
            account_detail = {
                "account": account,
                "balance": f"{account_value:,.2f}",
            }
            accounts_detail.append(account_detail)
        print(accounts_detail)

    if request.method == "POST":
        form = AccountForm(request.POST, user=request.user)
        if form.is_valid():
            account_name = form.clean_name()
            account = Account(
                user=request.user,
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
def delete_object(request, model, id, redirect_url, object_type):
    """
    Generic view to delete an object.
    Args:
        model: The model class of the object to delete.
        object_id: The primary key or unique identifier of the object.
        redirect_url: The URL name to redirect to after deletion.
        object_type: A string representing the type of object (e.g., "Account", "Address").
    """
    obj = get_object_or_404(model, pk=id)

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
def addresses(request):
    addresses_detail = []
    addresses = Address.objects.filter(user=request.user)
    for address in addresses:
        addresses = [address]
        address_value = calculate_total_value(addresses)
        address_detail = {
            "address": address,
            "balance": f"{address_value:,.2f}",
        }
        addresses_detail.append(address_detail)
    print(addresses_detail)

    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            public_address = form.clean_public_address()
            if Web3.is_checksum_address(public_address) is False:
                public_address = Web3.to_checksum_address(public_address)

            address = Address(
                user=request.user,
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
def address_detail(request, public_address):
    address = Address.objects.get(public_address=public_address)
    addresses = [address]
    aggregated_assets = fetch_aggregated_assets(addresses)
    total_eth_staking = get_aggregated_staking(addresses)
    total_liquity_v1 = get_protocols_snapshots(addresses, protocol_name="Liquity V1")
    total_liquity_v2 = get_protocols_snapshots(addresses, protocol_name="Liquity V2")
    total_aave = get_protocols_snapshots(addresses, protocol_name="Aave V3")
    portfolio_value = calculate_total_value(addresses)

    last_snapshot = Snapshot.objects.first()
    if last_snapshot:
        last_snapshot = last_snapshot.date
    else:
        last_snapshot = None
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
        "last_snapshot": last_snapshot,
        "address": address,
    }
    return render(request, "address_detail.html", context)


@login_required()
def rewards(request):
    """
    Show rewards for the portafolio, include staking rewards and protocol rewards.
    """

    addresses = Address.objects.filter(user=request.user)

    # Get ETH Staking rewards
    eth_rewards = 0
    validators = get_last_validators(addresses)
    for validator in validators:
        current_price = get_last_price(
            "ethereum", snapshot=validator.snapshot.date
        )
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
def edit_object(request, model, id, form, redirect_url, object_type):
    """
    Generic view to edit an object.
    Args:
        model: The model class of the object to edit.
        id: The primary key or unique identifier of the object.
        form: The form class for editing the object.
        redirect_url: The URL name to redirect to after editing.
    """
    obj = get_object_or_404(model, pk=id)
    print (obj)

    if request.method == "POST":
        form = form(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = form(instance=obj)

    # Render the edit page
    context = {
        "form2": form,
        "object": obj,
        "object_type": object_type,
    }
    return render(request, "edit_object.html", context)


def logout_view(request):
    logout(request)


@login_required()
def refresh(request):
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
def waiting_page(request):
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
def check_task_status(request):
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
def statistics(request):
    """
    Show some statistics of the portfolio.
    """
    addresses = Address.objects.filter(user=request.user)

    # Statistic balance per type of wallet

    wallet_types = ["HOT", "COLD", "SMART"]

    for wallet in wallet_types:
        calculate_total_value(addresses.filter(wallet_type=wallet))

    wallet_values = {
        wallet: calculate_total_value(addresses.filter(wallet_type=wallet))
        for wallet in wallet_types
    }

    # Amount (EUR) per account
    accounts_detail = []
    accounts = Account.objects.filter(user=request.user)
    for account in accounts:
        account_addresses = Address.objects.filter(account=account)
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
