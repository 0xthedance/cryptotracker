from django.core.management.base import BaseCommand

from cryptotracker.models import Network

from cryptotracker.constants import NETWORKS


class Command(BaseCommand):
    help = "Initialize networks"

    def handle(self, *args, **options):
        for network in NETWORKS.values():
            network_obj, created = Network.objects.get_or_create(
                name=network["name"],
                defaults={
                    "url_rpc": network["url_rpc"],
                    "image": network["image"],
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created network: {network['name']}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Network already exists: {network['name']}")
                )
        self.stdout.write(self.style.SUCCESS("All networks initialized successfully!"))
