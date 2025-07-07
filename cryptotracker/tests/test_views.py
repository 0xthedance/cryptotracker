from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from cryptotracker.models import Account, UserAddress, WalletType


class CryptoTrackerViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("initialize_db")

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        # Create wallet types
        self.wallet_type = WalletType.objects.get(name="HOT")

        # Create an account
        self.account = Account.objects.create(user=self.user, name="Test Account")

        # Create an user_address
        self.user_address = UserAddress.objects.create(
            user=self.user,
            public_address="0x1234567890abcdef1234567890abcdef12345678",
            account=self.account,
            wallet_type=self.wallet_type,
            name="Test UserAddress",
        )

    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crypto Tracker")

    def test_portfolio_view(self):
        response = self.client.get(reverse("portfolio"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Portfolio")

    def test_addresses_view(self):
        response = self.client.get(reverse("user_addresses"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Addresses")
        self.assertContains(response, self.user_address.public_address)

    def test_add_address_view(self):
        response = self.client.post(
            reverse("user_addresses"),
            {
                "public_address": "0x20e1012610b9212d45ef0A3af40843D5CA121FD0",
                "wallet_type": self.wallet_type.id,
                "name": "New UserAddress",
                "account": self.account.id,
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful addition
        self.assertTrue(UserAddress.objects.filter(name="New UserAddress").exists())

    def test_delete_address_view(self):
        response = self.client.post(
            reverse("delete_address", args=[self.user_address.id])
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful deletion
        self.assertFalse(UserAddress.objects.filter(id=self.user_address.id).exists())

    def test_accounts_view(self):
        response = self.client.get(reverse("accounts"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accounts")
        self.assertContains(response, self.account.name)

    def test_add_account_view(self):
        response = self.client.post(
            reverse("accounts"),
            {"name": "New Account"},
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful addition
        self.assertTrue(Account.objects.filter(name="New Account").exists())

    def test_delete_account_view(self):
        response = self.client.post(reverse("delete_account", args=[self.account.id]))
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful deletion
        self.assertFalse(Account.objects.filter(id=self.account.id).exists())

    def test_refresh_view(self):
        response = self.client.get(reverse("refresh"))
        self.assertEqual(response.status_code, 302)  # Redirect to waiting page

    def test_statistics_view(self):
        response = self.client.get(reverse("statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Statistics")
