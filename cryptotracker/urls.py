from django.urls import include, path

from cryptotracker.views import (
    account_detail,
    accounts,
    delete_account,
    home,
    portfolio,
    sign_up,
    refresh,
    staking,
    edit_account,
)

urlpatterns = [
    path("", home, name="home"),
    path("portfolio/", portfolio, name="portfolio"),
    path("accounts/", accounts, name="accounts"),
    path("account/<str:public_address>/", account_detail, name="account_detail"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("sign_up/", sign_up, name="sign_up"),
    path("account/<str:public_address>/delete/", delete_account, name="delete_account"),
    path("refresh/", refresh, name="refresh"),
    path("staking/", staking, name="staking"),
    path("account/<str:public_address>/edit/", edit_account, name="edit_account"),
]
