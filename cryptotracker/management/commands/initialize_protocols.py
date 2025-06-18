from django.core.management.base import BaseCommand

from cryptotracker.models import Network, Pool, PoolType, Protocol, ProtocolNetwork

PROTOCOLS = [
    {
        "name": "Liquity v1",
        "image": "cryptotracker/logos/liquity_v1.png",
        "Ethereum": [
            {
                "name": "staking",
                "contract_address": "0x4f9Fbb3f1E99B56e0Fe2892e623Ed36A76Fc605d",
                "image": "cryptotracker/logos/liquity_staking.png",
            },
            {
                "name": "stability pool",
                "contract_address": "0x66017D22b0f8556afDd19FC67041899Eb65a21bb",
                "image": "cryptotracker/logos/liquity_stability_pool.png",
            },
            {
                "name": "borrowing",
                "contract_address": None,
                "image": "cryptotracker/logos/liquity_borrow.png",
            },
        ],
    },
    {
        "name": "Liquity v2",
        "image": "cryptotracker/logos/liquity_v2.png",
        "Ethereum": [
            {
                "name": "borrowing",
                "contract_address": None,
                "image": "cryptotracker/logos/liquity_borrow_v2.png",
            },
            {
                "name": "staking",
                "contract_address": "0x807def5e7d057df05c796f4bc75c3fe82bd6eee1",
                "image": "cryptotracker/logos/liquity_staking_v2.png",
            },
            {
                "name": "stability pool",
                "contract_address": "0x5721cbbd64fc7ae3ef44a0a3f9a790a9264cf9bf",
                "image": "cryptotracker/logos/liquity_stability_pool_weth.png",
                "description": "WETH",
            },
            {
                "name": "stability pool",
                "contract_address": "0x9502b7c397e9aa22fe9db7ef7daf21cd2aebe56b",
                "image": "cryptotracker/logos/liquity_stability_pool_lido.png",
                "description": "wstETH",
            },
            {
                "name": "stability pool",
                "contract_address": "0xd442e41019b7f5c4dd78f50dc03726c446148695",
                "image": "cryptotracker/logos/liquity_stability_pool_reth.png",
                "description": "rETH",
            },
        ],
    },
    {
        "name": "Aave v3",
        "image": "cryptotracker/logos/aave.png",
        "Ethereum": [
            {
                "name": "lending",
                "contract_address": "0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e",
            },
        ],
        "Arbitrum": [
            {
                "name": "lending",
                "contract_address": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb",
            },
        ],
        "Avalanche": [
            {
                "name": "lending",
                "contract_address": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb",
            },
        ],
        "Gnosis Chain": [
            {
                "name": "lending",
                "contract_address": "0x36616cf17557639614c1cdDb356b1B83fc0B2132",
            },
        ],
        "Base": [
            {
                "name": "lending",
                "contract_address": "0xe20fCBdBfFC4Dd138cE8b2E6FBb6CB49777ad64D",
            },
        ],
    },
    {
        "name": "Uniswap v3",
        "image": "cryptotracker/logos/uniswap.png",
        "Ethereum": [
            {
                "name": "AMM pool",
                "contract_address": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Initialize the protocols and pools in the application"

    def handle(self, *args, **options):
        # Create or get PoolTypes

        pool_types = [
            "staking",
            "stability pool",
            "borrowing",
            "staking",
            "lending",
            "AMM pool",
        ]
        for pool_type in pool_types:
            obj, created = PoolType.objects.get_or_create(name=pool_type)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added PoolType: {pool_type}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"PoolType '{pool_type}' already exists")
                )

        networks = Network.objects.all()

        for protocol_data in PROTOCOLS:
            # Create or get the Protocol
            protocol, created_protocol = Protocol.objects.get_or_create(
                name=protocol_data["name"],
                defaults={"image": protocol_data["image"]},
            )
            if created_protocol:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Added protocol {protocol.name} to the database."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Protocol {protocol.name} already exists.")
                )

            # Create ProtocolNetwork entries for each network
            for network in networks:
                protocol_network, created_protocol_network = (
                    ProtocolNetwork.objects.get_or_create(
                        protocol=protocol,
                        network=network,
                    )
                )
                if created_protocol_network:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Linked protocol {protocol.name} to network {network.name}."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Protocol {protocol.name} is already linked to network {network.name}."
                        )
                    )

                # Check if the network has pools defined in the protocol
                if network.name not in protocol_data:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No pools defined for {protocol.name} on {network.name}."
                        )
                    )
                    continue

                # Create or get the Pools for the protocol and network
                for pool_data in protocol_data[network.name]:
                    pool, created_pool = Pool.objects.get_or_create(
                        type=PoolType.objects.get(name=pool_data["name"]),
                        protocol_network=protocol_network,
                        contract_address=pool_data["contract_address"],
                        defaults={},
                    )
                    if created_pool:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Added pool {pool.type} for protocol {protocol.name} on network {network.name}."
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Pool {pool.type} for protocol {protocol.name} on network {network.name} already exists."
                            )
                        )
