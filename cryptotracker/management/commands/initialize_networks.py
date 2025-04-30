from django.core.management.base import BaseCommand
from cryptotracker.models import Network


NETWORKS = [
    {
    "name": "Ethereum",
    "url_rpc": "ethereum:mainnet:alchemy",
    "image": "cryptotracker/logos/ethereum.png",
    },
    {
    "name": "Arbitrum",
    "url_rpc": "arbitrum:mainnet:alchemy",
    "image": "cryptotracker/logos/arbitrum.png",
    },
    {
    "name": "Avalanche",
    "url_rpc": "avalanche:mainnet:alchemy",
    "image": "cryptotracker/logos/avalanche.png",
    },
    {
    "name": "Gnosis Chain",
    "url_rpc": "gnosis:mainnet:alchemy",
    "image": "cryptotracker/logos/gnosis.png",
    },
    {
    "name": "Base",
    "url_rpc": "base:mainnet:alchemy",
    "image": "cryptotracker/logos/base.png",
    },
]

class Command(BaseCommand):
    help = "Initialize networks"

    def handle(self, *args, **options):
        for network in NETWORKS:
            network_obj, created = Network.objects.get_or_create(
                name=network["name"],
                defaults={
                    "url_rpc": network["url_rpc"],
                    "image": network["image"],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created network: {network['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Network already exists: {network['name']}"))
        self.stdout.write(self.style.SUCCESS("All networks initialized successfully!"))

