from django.contrib import admin
from .models import Farmer, MilkCollection, Payment

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('user', 'rfid_number', 'phone_number')
    search_fields = ('user__first_name', 'user__last_name', 'rfid_number')

@admin.register(MilkCollection)
class MilkCollectionAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'date', 'quantity', 'fat_content', 'total_amount', 'session')
    list_filter = ('session', 'date')
    search_fields = ('farmer__user__first_name', 'farmer__user__last_name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('farmer__user__first_name', 'farmer__user__last_name') 