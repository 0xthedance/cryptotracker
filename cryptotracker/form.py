from django import forms
from django.forms import ModelForm

from cryptotracker.models import Account, Address


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ["name"]

    def clean_name(self):
        cleaned_data = super().clean()
        name = cleaned_data["name"]

        # Length check
        if len(name) < 3 or len(name) > 20:
            raise forms.ValidationError("Invalid account name length")

        # Existence check
        if Account.objects.filter(name=name).exists():
            raise forms.ValidationError("Account name already exists")

        return name


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ["public_address", "account", "wallet_type", "name"]

    def clean_public_address(self):

        cleaned_data = super().clean()
        public_address = cleaned_data["public_address"]

        # Length check
        if len(public_address) != 42:
            raise forms.ValidationError("Invalid public address length")

        # Prefix check
        if not public_address.startswith("0x"):
            raise forms.ValidationError("Invalid public address prefix")

        # Hexadecimal check
        try:
            int(public_address, 16)
        except ValueError:
            raise forms.ValidationError("Invalid public address hexadecimal")

        # Existence check
        if Address.objects.filter(public_address=public_address).exists():
            raise forms.ValidationError("Public address already exists")

        return public_address


class EditAddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ["wallet_type", "name"]
