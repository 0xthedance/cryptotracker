from django.core.management.base import BaseCommand

from cryptotracker.models import Cryptocurrency, CryptocurrencyNetwork, Network

from cryptotracker.constants import TOKENS


class Command(BaseCommand):
    help = "Initialize the database with tokens"

    def handle(self, *args, **kwargs):
        # Iterate through the tokens
        for token in TOKENS.values():
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
