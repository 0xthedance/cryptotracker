from django.contrib import admin

from cryptotracker.models import Account, Cryptocurrency, Network, Pool, Price, Protocol


# Register your models here.
class CryptocurrencyAdmin(admin.ModelAdmin):
    pass


class PriceAdmin(admin.ModelAdmin):
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
admin.site.register(Price, PriceAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Pool, PoolAdmin)
admin.site.register(Protocol, ProtocolAdmin)
