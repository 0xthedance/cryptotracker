from django.core.management.base import BaseCommand

from cryptotracker.models import Network, Pool, PoolType, Protocol, ProtocolNetwork
from cryptotracker.constants import PROTOCOLS_DATA, POOL_TYPES


class Command(BaseCommand):
    help = "Initialize the protocols and pools in the application"

    def handle(self, *args, **options):
        # Create or get PoolTypes

        for pool_type in POOL_TYPES.values():
            obj, created = PoolType.objects.get_or_create(name=pool_type)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added PoolType: {pool_type}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"PoolType '{pool_type}' already exists")
                )

        networks = Network.objects.all()

        for protocol_data in PROTOCOLS_DATA.values():
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
                        type=PoolType.objects.get(name=pool_data["type"]),
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
