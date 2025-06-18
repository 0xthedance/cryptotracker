from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Initialize the database with networks, wallet types, tokens, and protocols"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Initializing database..."))

        # Initialize wallet types
        self.stdout.write(self.style.SUCCESS("Initializing wallet types..."))
        call_command("initialize_wallet_types")

        # Initialize networks
        self.stdout.write(self.style.SUCCESS("Initializing networks..."))
        call_command("initialize_networks")

        # Initialize tokens
        self.stdout.write(self.style.SUCCESS("Initializing tokens..."))
        call_command("initialize_tokens")

        # Initialize protocols
        self.stdout.write(self.style.SUCCESS("Initializing protocols..."))
        call_command("initialize_protocols")

        self.stdout.write(self.style.SUCCESS("Database initialization complete!"))
