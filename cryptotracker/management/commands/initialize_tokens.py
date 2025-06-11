from django.core.management.base import BaseCommand
from cryptotracker.models import Cryptocurrency, CryptocurrencyNetwork, Network

TOKENS = [
    {
        "name": "ethereum",
        "symbol": "ETH",
        "image": "cryptotracker/logos/ethereum.png",
        "token_address": {
            "Ethereum": "0x",
            "Avalanche": None,
            "Arbitrum": "0x",
            "Gnosis Chain": "0x",
            "Base": "0x",
        },
    },
    {
        "name": "liquity",
        "symbol": "LQTY",
        "image": "cryptotracker/logos/liquity.png",
        "token_address": {
            "Ethereum": "0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D",
            "Avalanche": None,
            "Arbitrum": "0xfb9e5d956d889d91a82737b9bfcdac1dce3e1449",
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    {
        "name": "ssv-network",
        "symbol": "SSV",
        "image": "cryptotracker/logos/ssv.png",
        "token_address": {
            "Ethereum": "0x9D65fF81a3c488d585bBfb0Bfe3c7707c7917f54",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    {
        "name": "balancer",
        "symbol": "BAL",
        "image": "cryptotracker/logos/bal.png",
        "token_address": {
            "Ethereum": "0xba100000625a3754423978a60c9317c58a424e3d",
            "Avalanche": "0xe15bcb9e0ea69e6ab9fa080c4c4a5632896298c3",
            "Arbitrum": "0x040d1edc9569d4bab2d15287dc5a4f10f56a56b8",
            "Gnosis Chain": "0x7ef541e2a22058048904fe5744f9c7e4c57af717",
            "Base": "0x4158734d47fc9692176b5085e0f52ee0da5d47f1",
        },
    },
    {
        "name": "liquity-usd",
        "symbol": "LUSD",
        "image": "cryptotracker/logos/lusd.png",
        "token_address": {
            "Ethereum": "0x5f98805a4e8be255a32880fdec7f6728c6568ba0",
            "Avalanche": None,
            "Arbitrum": "0x93b346b6bc2548da6a1e7d98e9a421b42541425b",
            "Gnosis Chain": None,
            "Base": "0x368181499736d0c0cc614dbb145e2ec1ac86b8c6",
        },
    },
    {
        "name": "safe",
        "symbol": "SAFE",
        "image": "cryptotracker/logos/safe.png",
        "token_address": {
            "Ethereum": "0x5afe3855358e112b5647b952709e6165e1c1eeee",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": "0x4d18815d14fe5c3304e87b3fa18318baa5c23820",
            "Base": None,
        },
    },
    {
        "name": "arbitrum",
        "symbol": "ARB",
        "image": "cryptotracker/logos/arbitrum.png",
        "token_address": {
            "Ethereum": "0xb50721bcf8d664c30412cfbc6cf7a15145234ad1",
            "Avalanche": None,
            "Arbitrum": "0x912ce59144191c1204e64559fe8253a0e49e6548",
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    {
        "name": "liquity-bold",
        "symbol": "BOLD",
        "image": "cryptotracker/logos/bold.png",
        "token_address": {
            "Ethereum": "0xb01dd87b29d187f3e3a4bf6cdaebfb97f3d9ab98",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    {
        "name": "weth",
        "symbol": "WETH",
        "image": "cryptotracker/logos/WETH.png",
        "token_address": {
            "Ethereum": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    {
        "name": "wrapped-steth",
        "symbol": "wstETH",
        "image": "cryptotracker/logos/wstETH.png",
        "token_address": {
            "Ethereum": "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    {
        "name": "rocket-pool-eth",
        "symbol": "rETH",
        "image": "cryptotracker/logos/rETH.png",
        "token_address": {
            "Ethereum": "0xae78736cd615f374d3085123a210448e74fc6393",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": None,
            "Base": None,
        },
    },
        {
        "name": "usd-coin",
        "symbol": "USDC",
        "image": "cryptotracker/logos/USDC.png",
        "token_address": {
            "Ethereum": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "Avalanche": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
            "Arbitrum": "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
            "Gnosis Chain": None,
            "Base": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
        },
    },
]


class Command(BaseCommand):
    help = "Initialize the database with tokens"

    def handle(self, *args, **kwargs):
        # Iterate through the tokens
        for token in TOKENS:
            # Create or get the Cryptocurrency
            cryptocurrency, created_crypto = Cryptocurrency.objects.get_or_create(
                name=token["name"],
                symbol=token["symbol"],
                defaults={"image": token["image"]},
            )
            if created_crypto:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Added cryptocurrency {token['name']} to the database."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Cryptocurrency {token['name']} already exists."
                    )
                )

            # Iterate through the networks and token_addresses
            for network_name, token_address in token["token_address"].items():
                if not token_address:  # Skip if the token_address is empty
                    continue

                # Get the network
                network = Network.objects.get(name=network_name)

                # Create or get the CryptocurrencyNetwork
                crypto_network, created_network = (
                    CryptocurrencyNetwork.objects.get_or_create(
                        cryptocurrency=cryptocurrency,
                        network=network,
                        token_address=token_address,
                    )
                )
                if created_network:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Added {token['name']} on {network_name} network to the database."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"{token['name']} on {network_name} network already exists."
                        )
                    )
