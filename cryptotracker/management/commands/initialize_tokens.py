from django.core.management.base import BaseCommand
from cryptotracker.models import Cryptocurrency


TOKENS = [
    {
        "name": "ethereum",
        "symbol": "ETH",
        "image": "cryptotracker/logos/ethereum.png",
        "address": "0x",
    },
    {
        "name": "liquity",
        "symbol": "LQTY",
        "image": "cryptotracker/logos/liquity.png",
        "address": "0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D",
    },
    {
        "name": "ssv-network",
        "symbol": "SSV",
        "image": "cryptotracker/logos/ssv.png",
        "address": "0x9D65fF81a3c488d585bBfb0Bfe3c7707c7917f54",
    },
    {
        "name": "balancer",
        "symbol": "BAL",
        "image": "cryptotracker/logos/bal.png",
        "address": "0xba100000625a3754423978a60c9317c58a424e3d",
    },
    {
        "name": "liquity-usd",
        "symbol": "LUSD",
        "image": "cryptotracker/logos/lusd.png",
        "address": "0x5f98805a4e8be255a32880fdec7f6728c6568ba0",
    },
    {
        "name": "safe",
        "symbol": "SAFE",
        "image": "cryptotracker/logos/safe.png",
        "address": "0x5afe3855358e112b5647b952709e6165e1c1eeee",
    },
]


class Command(BaseCommand):
    help = "Initialize the database with tokens"

    def handle(self, *args, **kwargs):
        # Check if the tokens are already initialized
        for token in TOKENS:
            obj, created = Cryptocurrency.objects.get_or_create(
                address=token["address"],
                defaults={
                    "name": token["name"],
                    "symbol": token["symbol"],
                    "image": token["image"],
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Added {token['name']} to the database.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"{token['name']} already exists in the database."
                    )
                )
