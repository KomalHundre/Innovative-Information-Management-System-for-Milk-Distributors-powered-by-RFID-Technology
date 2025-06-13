from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

def validate_phone_length(value):
    if len(value) != 10:
        raise ValidationError('Phone number must be exactly 10 digits.')
    if not value.isdigit():
        raise ValidationError('Phone number must contain only digits.')
    if not value[0] in '6789':
        raise ValidationError('Phone number must start with 6, 7, 8, or 9.')

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dairy_collection_farmer')
    rfid_number = models.CharField(max_length=50, unique=True)
    
    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[validate_phone_length],
        error_messages={
            'invalid': 'Enter a valid 10-digit phone number.',
            'unique': 'This phone number is already registered.'
        },
        help_text="Enter a 10-digit mobile number starting with 6, 7, 8, or 9"
    )
    
    # Bank account validation - only allow numeric values between 9-18 digits
    bank_account_regex = RegexValidator(
        regex=r'^\d{9,18}$',
        message="Bank account number must be between 9 and 18 digits"
    )
    bank_account_number = models.CharField(validators=[bank_account_regex], max_length=18, unique=True)
    
    # IFSC code validation - must follow Indian bank IFSC format
    ifsc_regex = RegexValidator(
        regex=r'^[A-Z]{4}0[A-Z0-9]{6}$',
        message="IFSC code must be valid format: 4 letters followed by 0 and 6 alphanumeric characters"
    )
    ifsc_code = models.CharField(validators=[ifsc_regex], max_length=11)
    address = models.TextField()
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    class Meta:
        ordering = ['user__first_name']

class MilkRate(models.Model):
    MILK_TYPE_CHOICES = [
        ('cow', 'Cow Milk'),
        ('buffalo', 'Buffalo Milk')
    ]
    
    milk_type = models.CharField(max_length=10, choices=MILK_TYPE_CHOICES)
    min_fat = models.DecimalField(max_digits=3, decimal_places=1, help_text="Minimum fat percentage for this rate")
    max_fat = models.DecimalField(max_digits=3, decimal_places=1, help_text="Maximum fat percentage for this rate")
    base_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Base rate per liter")
    fat_multiplier = models.DecimalField(max_digits=5, decimal_places=2, help_text="Rate multiplier per 0.1% fat")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_milk_type_display()} - {self.min_fat}% to {self.max_fat}% fat"
    
    class Meta:
        ordering = ['milk_type', 'min_fat']
        unique_together = ['milk_type', 'min_fat', 'max_fat']
    
    def calculate_rate(self, fat_content):
        """Calculate rate based on fat content"""
        if self.min_fat <= fat_content <= self.max_fat:
            # Calculate additional rate based on fat content
            fat_diff = fat_content - self.min_fat
            additional_rate = (fat_diff / 0.1) * self.fat_multiplier
            return self.base_rate + additional_rate
        return None

class MilkCollection(models.Model):
    MILK_TYPE_CHOICES = [
        ('cow', 'Cow Milk'),
        ('buffalo', 'Buffalo Milk')
    ]
    SESSION_CHOICES = [
        ('morning', 'Morning'),
        ('evening', 'Evening')
    ]
    
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    milk_type = models.CharField(max_length=10, choices=MILK_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    fat_content = models.DecimalField(max_digits=3, decimal_places=1)
    snf_content = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    price_per_liter = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    session = models.CharField(max_length=10, choices=SESSION_CHOICES)
    sms_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.farmer} - {self.date.strftime('%Y-%m-%d')} {self.session}"
    
    class Meta:
        ordering = ['-date']
        # Ensure only one collection per farmer per session per day
        unique_together = ['farmer', 'date', 'session']
    
    def calculate_price(self):
        """Calculate price based on fat content"""
        try:
            fat = round(float(self.fat_content) * 10) / 10  # Round to nearest 0.1
            
            # Base price chart
            price_chart = {
                3.5: 29.00, 3.6: 29.30, 3.7: 29.60, 3.8: 29.90, 3.9: 30.20, 4.0: 30.50,
                4.1: 30.80, 4.2: 31.10, 4.3: 31.40, 4.4: 31.70, 4.5: 32.00, 4.6: 32.30,
                4.7: 32.60, 4.8: 32.90, 4.9: 33.20, 5.0: 33.50, 5.1: 33.80, 5.2: 34.10,
                5.3: 34.40, 5.4: 34.70, 5.5: 35.00, 5.6: 35.30, 5.7: 35.60, 5.8: 35.90,
                5.9: 36.20, 6.0: 36.50
            }
            
            # If exact match in price chart
            if fat in price_chart:
                price_per_liter = price_chart[fat]
            # For values between chart points
            elif 3.5 <= fat <= 6.0:
                lower_fat = float(int(fat * 10) / 10)  # Get nearest lower fat percentage
                if lower_fat in price_chart:
                    base_price = price_chart[lower_fat]
                    increment = 0.30  # ₹0.30 per 0.1% fat
                    fat_diff = (fat - lower_fat) * 10  # Difference in 0.1% units
                    price_per_liter = base_price + (increment * fat_diff)
            # For fat content above price chart
            elif fat > 6.0:
                price_per_liter = 36.50 + ((fat - 6.0) * 3)  # ₹3 increase per 1% above 6%
            else:
                return False
                
            self.price_per_liter = round(price_per_liter, 2)
            self.total_amount = round(self.quantity * self.price_per_liter, 2)
            return True
        except Exception as e:
            print(f"Error calculating price: {str(e)}")
            return False

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Cash", "Bank Transfer", "UPI"
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]
    
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.farmer} - ₹{self.amount} ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']

class WeeklyReport(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_quantity = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    average_fat = models.DecimalField(max_digits=3, decimal_places=1)
    average_snf = models.DecimalField(max_digits=3, decimal_places=1)
    collection_count = models.IntegerField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.farmer} - Week of {self.start_date}"
    
    class Meta:
        ordering = ['-start_date']
        unique_together = ['farmer', 'start_date']

class Notification(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.farmer} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']

class FatBasedPrice(models.Model):
    fat_percentage = models.DecimalField(
        max_digits=3, 
        decimal_places=1,
        unique=True,
        help_text="Fat percentage (e.g., 3.5)"
    )
    price = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Price per liter in rupees"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fat_percentage']
        verbose_name = 'Fat Based Price'
        verbose_name_plural = 'Fat Based Prices'

    def __str__(self):
        return f"{self.fat_percentage}% - ₹{self.price}"

    @staticmethod
    def get_price_for_fat(fat_percentage):
        """Get price for given fat percentage"""
        try:
            # Round to nearest 0.1
            fat = Decimal(str(fat_percentage)).quantize(Decimal('0.1'))
            price_obj = FatBasedPrice.objects.filter(
                fat_percentage=fat,
                is_active=True
            ).first()
            return price_obj.price if price_obj else None
        except Exception:
            return None

class SMSMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed')
    ]
    
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"SMS to {self.farmer} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'SMS Message'
        verbose_name_plural = 'SMS Messages'