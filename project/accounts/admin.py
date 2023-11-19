from django.contrib import admin
from .models import Account,Addresses,Country

# Register your models here


admin.site.register(Account)
admin.site.register(Addresses)
admin.site.register(Country)