from django.contrib import admin
from .models import Farmer, MilkCollection, Payment, FatBasedPrice

@admin.register(FatBasedPrice)
class FatBasedPriceAdmin(admin.ModelAdmin):
    list_display = ('fat_percentage', 'price', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('fat_percentage', 'price')
    ordering = ('fat_percentage',)
    list_editable = ('price', 'is_active')

admin.site.register(Farmer)
admin.site.register(MilkCollection)
admin.site.register(Payment) 