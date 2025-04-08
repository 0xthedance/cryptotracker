from django import forms
from django.forms import ModelForm

from cryptotracker.models import Account


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ["public_address"]

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
        if Account.objects.filter(public_address=public_address).exists():
            raise forms.ValidationError("Public address already exists")

        return public_address
