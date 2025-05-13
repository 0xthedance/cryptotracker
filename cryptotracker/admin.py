from django.contrib import admin
from cryptotracker.models import (
    Cryptocurrency,
    CryptocurrencyPrice,
    Account,
    Network,
    Pool,
    Protocol,
)


# Register your models here.
class CryptocurrencyAdmin(admin.ModelAdmin):
    pass


class CryptocurrencyPriceAdmin(admin.ModelAdmin):
    pass


class AccountAdmin(admin.ModelAdmin):
    pass


class NetworkAdmin(admin.ModelAdmin):
    pass


class PoolAdmin(admin.ModelAdmin):
    pass


class ProtocolAdmin(admin.ModelAdmin):
    pass


admin.site.register(Cryptocurrency, CryptocurrencyAdmin)
admin.site.register(CryptocurrencyPrice, CryptocurrencyPriceAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Pool, PoolAdmin)
admin.site.register(Protocol, ProtocolAdmin)
