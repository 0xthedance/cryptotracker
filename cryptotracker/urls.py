from django.urls import include, path

from cryptotracker.models import Account, Address

from cryptotracker.form import EditAddressForm, AccountForm

from cryptotracker.views import (
    address_detail,
    addresses,
    delete_object,
    home,
    portfolio,
    sign_up,
    refresh,
    staking,
    edit_object,
    accounts,
    waiting_page,
    check_task_status,
    rewards,
    statistics,
)

urlpatterns = [
    path("", home, name="home"),
    path("accounts/", accounts, name="accounts"),
    path("portfolio/", portfolio, name="portfolio"),
    path("addresses/", addresses, name="addresses"),
    path("address/<str:public_address>/", address_detail, name="address_detail"),
    path("addresses/", include("django.contrib.auth.urls")),
    path("sign_up/", sign_up, name="sign_up"),
    path(
        "address/<str:id>/delete/",
        delete_object,
        {"model": Address, "redirect_url": "addresses", "object_type": "Address"},
        name="delete_address",
    ),
    path(
        "account/<str:id>/delete/",
        delete_object,
        {"model": Account, "redirect_url": "accounts", "object_type": "Account"},
        name="delete_account",
    ),
    path("refresh/", refresh, name="refresh"),
    path("staking/", staking, name="staking"),
    path(
        "address/<str:id>/edit/",
        edit_object,
        {
            "model": Address,
            "redirect_url": "addresses",
            "form": EditAddressForm,
            "object_type": "Address",
        },
        name="edit_address",
    ),
    path(
        "account/<str:id>/edit/",
        edit_object,
        {
            "model": Account,
            "redirect_url": "accounts",
            "form": AccountForm,
            "object_type": "Account",
        },
        name="edit_account",
    ),
    path("waiting_page/", waiting_page, name="waiting_page"),
    path("check_task_status/", check_task_status, name="check_task_status"),
    path("rewards/", rewards, name="rewards"),
    path("statistics/", statistics, name="statistics"),
]
