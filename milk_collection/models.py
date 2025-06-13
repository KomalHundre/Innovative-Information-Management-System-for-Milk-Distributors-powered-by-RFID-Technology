from django.db import models
from django.contrib.auth.models import User

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rfid_number = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15)
    bank_account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    address = models.TextField()
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class MilkCollection(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    fat_content = models.DecimalField(max_digits=3, decimal_places=1)
    price_per_liter = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    session = models.CharField(max_length=10, choices=[('morning', 'Morning'), ('evening', 'Evening')])
    
    def __str__(self):
        return f"{self.farmer} - {self.date}"

class Payment(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed')
    ])
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.farmer} - {self.amount}" 