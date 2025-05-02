from django.core.management.base import BaseCommand
from cryptotracker.models import Network, Pool, Protocol

PROTOCOLS = [
    {
        "name": "Liquity V1",
        "Ethereum": [
            {
                "name": "staking",
                "address": "0x4f9Fbb3f1E99B56e0Fe2892e623Ed36A76Fc605d",
                "image": "cryptotracker/logos/liquity_staking.png",
            },
            {
                "name": "stability_pool",
                "address": "0x66017D22b0f8556afDd19FC67041899Eb65a21bb",
                "image": "cryptotracker/logos/liquity_stability_pool.png",
            },
        ],
    },
    {
        "name": "Liquity V2",
        "Ethereum": [
            {
                "name": "staking",
                "address": "0x636dEb767Cd7D0f15ca4aB8eA9a9b26E98B426AC",
                "image": "cryptotracker/logos/liquity_staking_v2.png",
            },
            {
                "name": "stability_pool_weth",
                "address": "0xF69eB8C0d95D4094c16686769460f678727393CF",
                "image": "cryptotracker/logos/liquity_stability_pool_weth.png",
            },
            {
                "name": "stability_pool_v2_lido",
                "address": "0xcF46dAB575c364A8b91bDA147720ff4361F4627f",
                "image": "cryptotracker/logos/liquity_stability_pool_lido.png",
            },
            {
                "name": "stability_pool_v2_reth",
                "address": "0xC4463b26bE1a6064000558a84EF9B6a58AbE4F7a",
                "image": "cryptotracker/logos/liquity_stability_pool_reth.png",
            },
        ],
    },
    {
        "name": "Aave V3",
        "Ethereum": [
            {
                "name": "lending_pool",
                "address": "0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e",
                "image": "cryptotracker/logos/aave.png",
            },
        ],
        "Arbitrum": [
            {
                "name": "lending_pool",
                "address": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb"
                "image": "cryptotracker/logos/aave.png",
            },
        ],
        "Avalanche": [
            {
                "name": "lending_pool",
                "address": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb",
                "image": "cryptotracker/logos/aave.png",
            },
        ],
        "Gnosis Chain": [
            {
                "name": "lending_pool",
                "address": "0x36616cf17557639614c1cdDb356b1B83fc0B2132",
                "image": "cryptotracker/logos/aave.png",
            },
        ],
        "Base": [
            {
                "name": "lending_pool",
                "address": "0xe20fCBdBfFC4Dd138cE8b2E6FBb6CB49777ad64D",
                "image": "cryptotracker/logos/aave.png",
            },
        ],
    },
    {
        "name": "Uniswap V3",
        "Ethereum": [
            {
                "name": "lending_pool",
                "address": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
                "image": "cryptotracker/logos/uniswap.png",
            },
        ],
    }

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
