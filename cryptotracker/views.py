from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from web3 import Web3

from cryptotracker.form import AccountForm
from cryptotracker.models import Account
from cryptotracker.staking import (
    get_aggregated_staking,
    get_rewards,
    get_validators_from_withdrawal,
    get_validators_info,
)
from cryptotracker.tokens import fetch_aggregated_assets, fetch_assets

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
    user = request.user
    context = {"user": user}
    return render(request, "portfolio.html", context)


@login_required()
def holdings(request):
    accounts = Account.objects.filter(user=request.user)
    aggregated_assets = fetch_aggregated_assets(accounts)

    total_eth_staking = get_aggregated_staking(accounts)
    context = {
        "user": request.user,
        "assets": aggregated_assets,
        "total_eth_staking": total_eth_staking,
        "accounts": accounts,
    }

    return render(request, "holdings.html", context)


def staking(request):
    accounts = Account.objects.filter(user=request.user)
    validators = []

    for account in accounts:
        validators.append(get_validators_from_withdrawal(account.public_address))
    validator_details_list = get_validators_info(validators)
    rewards = get_rewards(validators)

    context = {
        "user": request.user,
        "validator_details_list": validator_details_list,
        "accounts": accounts,
        "rewards": rewards,
    }

    return render(request, "staking.html", context)


@login_required()
def accounts(request):
    accounts = Account.objects.filter(user=request.user)

    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            public_address = form.clean_public_address()
            if Web3.is_checksum_address(public_address) is False:
                public_address = Web3.to_checksum_address(public_address)

            account = Account(
                user=request.user,
                public_address=public_address,
            )
            account.save()

    context = {
        "accounts": accounts,
        "form1": AccountForm(),
    }
    return render(request, "accounts.html", context)


@login_required()
def account_detail(request, public_address):
    account = Account.objects.get(public_address=public_address)

    assets = fetch_assets(str(account.public_address))
    total_eth_staking = get_aggregated_staking([account])
    context = {
        "account": account,
        "assets": assets,
        "total_eth_staking": total_eth_staking,
    }
    print(assets)
    return render(request, "account_detail.html", context)


@login_required()
def delete_account(request, public_address):
    if request.method == "POST":
        account = Account.objects.get(public_address=public_address)
        account.delete()
        return redirect("accounts")


def logout_view(request):
    logout(request)
