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
            {
                "name": "borrow",
                "address":"0x7b",
                "image" : "cryptotracker/logos/liquity_staking_v2.png",
            },
        ],
    },
    {
        "name": "Liquity V2",
        "Ethereum": [
            {
                "name": "borrow",
                "address":"0x0x",
                "image" : "cryptotracker/logos/liquity_staking_v2.png",
            },
            {
                "name": "staking",
                "address": "0x807def5e7d057df05c796f4bc75c3fe82bd6eee1",
                "image": "cryptotracker/logos/liquity_staking_v2.png",
            },
            {
                "name": "stability_pool_weth",
                "address": "0x5721cbbd64fc7ae3ef44a0a3f9a790a9264cf9bf",
                "image": "cryptotracker/logos/liquity_stability_pool_weth.png",
            },
            {
                "name": "stability_pool_lido",
                "address": "0x9502b7c397e9aa22fe9db7ef7daf21cd2aebe56b",
                "image": "cryptotracker/logos/liquity_stability_pool_lido.png",
            },
            {
                "name": "stability_pool_reth",
                "address": "0xd442e41019b7f5c4dd78f50dc03726c446148695",
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
                "address": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb",
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
    help = "Initialize the protocols in the aplication"

    def handle(self, *args, **options):
        networks = Network.objects.all()

        for network in networks:         
        # Initialize the Protocols model
            for protocol in PROTOCOLS:
                obj_protocol, created = Protocol.objects.get_or_create(
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
            
                # Check if the network has pools defined in the protocol
                if network.name not in protocol:
                    self.stdout.write(
                        self.style.WARNING(f"No pools defined for {protocol['name']} on {network.name}.")
                    )
                    continue

            # Initialize the Pool model
                for pool in protocol[network.name]:
                    obj, created = Pool.objects.get_or_create(
                        name=pool["name"],
                        protocol=obj_protocol,
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
