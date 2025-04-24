from django.contrib import admin
from cryptotracker.models import Cryptocurrency, CryptocurrencyPrice, Account


# Register your models here.
class CryptocurrencyAdmin(admin.ModelAdmin):
    pass


class CryptocurrencyPriceAdmin(admin.ModelAdmin):
    pass


class AccountAdmin(admin.ModelAdmin):
    pass


admin.site.register(Cryptocurrency, CryptocurrencyAdmin)
admin.site.register(CryptocurrencyPrice, CryptocurrencyPriceAdmin)
admin.site.register(Account, AccountAdmin)
