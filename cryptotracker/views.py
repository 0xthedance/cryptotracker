from django.shortcuts import render, redirect
from cryptotracker.models import Account
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from cryptotracker.utils import fetch_assets, fetch_aggregated_assets
from cryptotracker.form import AccountForm
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from web3 import Web3


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
     accounts= Account.objects.filter(user=request.user)
     aggregated_assets = fetch_aggregated_assets(accounts)
     context = {
         "user": request.user,
         "assets" : aggregated_assets,
         }
     
     return render(request, "holdings.html", context )



@login_required()
def accounts(request):
    accounts= Account.objects.filter(user=request.user)
        
    if request.method == 'POST':
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

    context={
        "accounts": accounts ,
        "form1": AccountForm(),
    }
    return render(request, "accounts.html",context)

@login_required()
def account_detail(request, public_address):
    account = Account.objects.get(public_address=public_address)

    assets = fetch_assets(str(account.public_address))
    context = {
        "account": account ,
        "assets" : assets,
}
    print (assets)
    return render(request, "account_detail.html",context)

@login_required()
def delete_account(request, public_address):
    if request.method == 'POST':
        account = Account.objects.get(public_address=public_address)
        account.delete()
        return redirect('accounts') 

def logout_view(request):
    logout(request)