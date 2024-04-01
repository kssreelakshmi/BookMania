from django.contrib import admin
from .models import Account, Addresses,UserProfile, ContactMessage,ShippingAddress

# Register your models here


admin.site.register(Account)
admin.site.register(Addresses)
admin.site.register(UserProfile)
admin.site.register(ShippingAddress)
admin.site.register(ContactMessage)