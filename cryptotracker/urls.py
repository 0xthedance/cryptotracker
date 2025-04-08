from django.urls import include, path

from cryptotracker.views import (
    account_detail,
    accounts,
    delete_account,
    holdings,
    home,
    portfolio,
    sign_up,
)

urlpatterns = [
    path("", home, name="home"),
    path("portfolio/", portfolio, name="portfolio"),
    path("accounts/", accounts, name="accounts"),
    path("account/<str:public_address>/", account_detail, name="account_detail"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("sign_up/", sign_up, name="sign_up"),
    path("holdings/", holdings, name="holdings"),
    path("account/<str:public_address>/delete/", delete_account, name="delete_account"),
]
