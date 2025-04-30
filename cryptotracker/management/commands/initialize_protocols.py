from django.core.management.base import BaseCommand
from cryptotracker.models import Network, Pool, Protocol


NETWORKS = [
    {
    "name": "Ethereum_mainnet",
    }
]

PROTOCOLS = [
    {
    "name": "Liquity V1",
    "network": "Ethereum_mainnet",
    },
    {
    "name": "Liquity V2",
    "network": "Ethereum_mainnet",
    },

]

POOL = [
    {
    "name": "Staking",
    "protocol": "Liquity V1",
    "network": "Ethereum_mainnet",
    "address": "",
    "image": "cryptotracker/logos/liquity.png",
    },
    {
    "name": "Staking",
    "protocol": "Liquity V2",
    "network": "Ethereum_mainnet",
    "address": "",
    "image": "cryptotracker/logos/liquity.png",
    },
    {
    "name": "Stability Pool WETH",
    "protocol": "Liquity V2",
    "network": "Ethereum_mainnet",
    "address": "",
    "image": "cryptotracker/logos/liquity.png",
    },
    {
    "name": "Stability Pool V2 Lido",
    "protocol": "Liquity V2",
    "network": "Ethereum_mainnet",
    "address": "",
    "image": "cryptotracker/logos/liquity.png",
    },
    {
    "name": "Stability Pool V2 RETH",
    "protocol": "Liquity V2",
    "network": "Ethereum_mainnet",
    "address": "",
    "image": "cryptotracker/logos/liquity.png",
    },
]

class Command(BaseCommand):
    help = "Initialize the Liquity protocol and LUSD pool"

    def handle(self, *args, **options):
        # Initialize the Networks model
        for network in NETWORKS:
            obj, created = Network.objects.get_or_create(
                name=network["name"],
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Added {network['name']} to the database.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"{network['name']} already exists in the database.")
                )
        # Initialize the Protocols model
        for protocol in PROTOCOLS:
            network = Network.objects.get(name=protocol["network"])
            obj, created = Protocol.objects.get_or_create(
                name=protocol["name"],
                network=network,
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Added {protocol['name']} to the database.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"{protocol['name']} already exists in the database.")
                )
        # Initialize the Pool model
        for pool in POOL:
            network = Network.objects.get(name=pool["network"])
            protocol = Protocol.objects.get(name=pool["protocol"], network=network)
            obj, created = Pool.objects.get_or_create(
                name=pool["name"],
                protocol=protocol,
                network=network,
                address=pool["address"],
                image=pool["image"],
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Added {pool['name']} to the database.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"{pool['name']} already exists in the database.")
                )
        self.stdout.write(self.style.SUCCESS("All protocols and pools initialized."))
