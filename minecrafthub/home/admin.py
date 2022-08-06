from django.contrib import admin
from .models import ContactUs

# Register your models here.

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ("name", "email","registered_on")
    list_filter = ("registered_on",)
    search_fields = ["name", "email", "message"]


admin.site.site_header = 'BULKYSTAR'
admin.site.site_title = 'ADMIN SITE'
admin.site.index_title = 'DASHBOARD'
