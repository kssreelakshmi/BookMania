from django.contrib import admin
from .models import Account, Addresses,UserProfile, ContactMessage

# Register your models here


admin.site.register(Account)
admin.site.register(Addresses)
admin.site.register(UserProfile)
admin.site.register(ContactMessage)