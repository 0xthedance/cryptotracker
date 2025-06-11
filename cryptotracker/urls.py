from django.urls import include, path

from cryptotracker.models import Account, UserAddress

from cryptotracker.form import EditUserAddressForm, AccountForm

from cryptotracker.views import (
    address_detail,
    user_addresses,
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
    path("user_addresses/", user_addresses, name="user_addresses"),
    path("user_address/<str:public_address>/", address_detail, name="address_detail"),
    path("user_addresses/", include("django.contrib.auth.urls")),
    path("sign_up/", sign_up, name="sign_up"),
    path(
        "user_address/<str:id>/delete/",
        delete_object,
        {"model": UserAddress, "redirect_url": "user_addresses", "object_type": "UserAddress"},
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
        "user_address/<str:id>/edit/",
        edit_object,
        {
            "model": UserAddress,
            "redirect_url": "user_addresses",
            "form": EditUserAddressForm,
            "object_type": "UserAddress",
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
