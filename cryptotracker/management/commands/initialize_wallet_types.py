from django.core.management.base import BaseCommand
from cryptotracker.models import WalletType


class Command( BaseCommand):
    help="Initialize the Wallet Type table with the default values HOT, COLD, SMART"

    def handle(self, *args, **options):
        wallet_types = [ "HOT", "COLD", "SMART"]
        for wallet_type in wallet_types:

            obj, created = WalletType.objects.get_or_create (name = wallet_type)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added WalletType: {wallet_type}"))
            else:
                self.stdout.write(self.style.WARNING(f"WalletType '{wallet_type}' already exists"))