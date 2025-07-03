from django import forms
from django.forms import ModelForm

from cryptotracker.models import Account, UserAddress


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        cleaned_data = super().clean()
        name = cleaned_data["name"]

        # Length check
        if len(name) < 3 or len(name) > 20:
            raise forms.ValidationError("Invalid account name length")

        # Existence check for the same user
        if Account.objects.filter(name=name, user=self.user).exists():
            raise forms.ValidationError("You already have an account with this name")

        return name


class UserAddressForm(ModelForm):
    class Meta:
        model = UserAddress
        fields = ["public_address", "account", "wallet_type", "name"]

    def clean_public_address(self):
        cleaned_data = super().clean()
        public_address = cleaned_data["public_address"]

        # Length check
        if len(public_address) != 42:
            raise forms.ValidationError("Invalid public user_address length")

        # Prefix check
        if not public_address.startswith("0x"):
            raise forms.ValidationError("Invalid public user_address prefix")

        # Hexadecimal check
        try:
            int(public_address, 16)
        except ValueError:
            raise forms.ValidationError("Invalid public user_address hexadecimal")

        # Existence check
        if UserAddress.objects.filter(public_address=public_address).exists():
            raise forms.ValidationError("Public user_address already exists")

        return public_address


class EditUserAddressForm(ModelForm):
    class Meta:
        model = UserAddress
        fields = ["account", "wallet_type", "name"]
