from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from web3 import Web3

from cryptotracker.form import AccountForm, EditAccountForm
from cryptotracker.models import Account, SnapshotDate, SnapshotETHValidator
from cryptotracker.staking import (
    get_aggregated_staking,
    get_rewards,
    get_validators_from_withdrawal,
    get_validators_info,
    get_last_validators,
)

from cryptotracker.tokens import (
    fetch_aggregated_assets,
    fetch_assets,
)
from cryptotracker.tasks import update_assets_database, update_staking_assets
from cryptotracker.utils import get_total_value


# Create your views here.


def sign_up(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("portafolio_home"))
    else:
        form = UserCreationForm()
    return render(request, "registration/sign_up.html", {"form": form})


def home(request):
    return render(request, "home.html")


@login_required()
def portfolio(request):
    accounts = Account.objects.filter(user=request.user)
    aggregated_assets = fetch_aggregated_assets(accounts)
    total_eth_staking = get_aggregated_staking(accounts)
    portfolio_value = get_total_value(aggregated_assets, total_eth_staking)

    # Format the amounts for display
    if aggregated_assets:
        for key, value in aggregated_assets.items():
            value["amount"] = f"{value['amount']:,.2f}"
            value["amount_eur"] = f"{value['amount_eur']:,.2f}"
    # Format the total ETH staking balance
    if total_eth_staking:
        total_eth_staking["balance"] = f"{total_eth_staking['balance']:,.2f}"
        total_eth_staking["balance_eur"] = f"{total_eth_staking['balance_eur']:,.2f}"
        total_eth_staking["rewards"] = f"{total_eth_staking['rewards']:,.2f}"

    last_snapshot_date = (
        SnapshotDate.objects.filter(account__in=accounts).order_by("-date").first()
    )
    if last_snapshot_date:
        last_snapshot_date = last_snapshot_date.date
    else:
        last_snapshot_date = None
    context = {
        "user": request.user,
        "assets": aggregated_assets,
        "total_eth_staking": total_eth_staking,
        "accounts": accounts,
        "portfolio_value": f"{portfolio_value:,.2f}",
        "last_snapshot_date": last_snapshot_date,
    }

    return render(request, "portfolio.html", context)


@login_required()
def staking(request):
    accounts = Account.objects.filter(user=request.user)
    validators = get_last_validators(accounts)

    context = {
        "validators": validators,
    }
    return render(request, "staking.html", context)


@login_required()
def accounts(request):
    accounts_detail = []
    accounts = Account.objects.filter(user=request.user)

    for account in accounts:
        accounts = [account]
        aggregated_assets = fetch_aggregated_assets(accounts)
        total_eth_staking = get_aggregated_staking(accounts)
        account_value = get_total_value(aggregated_assets, total_eth_staking)
        account_detail = {
            "account": account,
            "balance": f"{account_value:,.2f}",
        }
        accounts_detail.append(account_detail)
    print(accounts_detail)

    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            public_address = form.clean_public_address()
            if Web3.is_checksum_address(public_address) is False:
                public_address = Web3.to_checksum_address(public_address)

            account = Account(
                user=request.user,
                public_address=public_address,
                wallet_type=form.cleaned_data["wallet_type"],
                name=form.cleaned_data["name"],
            )
            account.save()

    context = {
        "accounts_detail": accounts_detail,
        "form1": AccountForm(),
    }
    return render(request, "accounts.html", context)


@login_required()
def account_detail(request, public_address):
    account = Account.objects.get(public_address=public_address)
    accounts = [account]
    aggregated_assets = fetch_aggregated_assets(accounts)
    total_eth_staking = get_aggregated_staking(accounts)
    portfolio_value = get_total_value(aggregated_assets, total_eth_staking)

    # Format the amounts for display
    if aggregated_assets:
        for key, value in aggregated_assets.items():
            value["amount"] = f"{value['amount']:,.2f}"
            value["amount_eur"] = f"{value['amount_eur']:,.2f}"
    # Format the total ETH staking balance
    if total_eth_staking:
        total_eth_staking["balance"] = f"{total_eth_staking['balance']:,.2f}"
        total_eth_staking["balance_eur"] = f"{total_eth_staking['balance_eur']:,.2f}"
        total_eth_staking["rewards"] = f"{total_eth_staking['rewards']:,.2f}"

    last_snapshot_date = (
        SnapshotDate.objects.filter(account__in=accounts).order_by("-date").first()
    )
    if last_snapshot_date:
        last_snapshot_date = last_snapshot_date.date
    else:
        last_snapshot_date = None
    context = {
        "user": request.user,
        "assets": aggregated_assets,
        "total_eth_staking": total_eth_staking,
        "accounts": accounts,
        "portfolio_value": f"{portfolio_value:,.2f}",
        "last_snapshot_date": last_snapshot_date,
        "account": account,
    }
    return render(request, "account_detail.html", context)


@login_required()
def delete_account(request, public_address):
    account = Account.objects.get(public_address=public_address)

    if request.method == "POST":
        account.delete()
        return redirect(reverse("accounts"))

    # Render a confirmation page for GET requests
    return render(request, "confirm_delete.html", {"account": account})


@login_required()
def edit_account(request, public_address):
    account = Account.objects.get(public_address=public_address)
    print(account)
    if request.method == "POST":
        print(request.POST)
        form = EditAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect("accounts")
    else:
        form = EditAccountForm(instance=account)

    context = {
        "form2": form,
        "account": account,
    }
    return render(request, "edit_account.html", context)


def logout_view(request):
    logout(request)


@login_required()
def refresh(request):
    """
    accounts = Account.objects.filter(user=request.user)
    for account in accounts:
    # Trigger the task asynchronously
    """
    update_assets_database.delay()
    update_staking_assets.delay()
    return redirect(reverse("portfolio"))
