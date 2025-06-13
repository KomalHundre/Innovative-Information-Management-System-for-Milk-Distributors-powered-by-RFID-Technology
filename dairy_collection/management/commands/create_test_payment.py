from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from dairy_collection.models import Payment, Farmer, PaymentMethod
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a test payment'

    def handle(self, *args, **options):
        # Get the first farmer
        farmer = Farmer.objects.first()
        if not farmer:
            self.stdout.write(self.style.ERROR('No farmers found in the database'))
            return
        
        # Get or create a payment method
        payment_method, created = PaymentMethod.objects.get_or_create(
            name='Bank Transfer',
            defaults={'is_active': True}
        )
        
        # Get or create a staff user for processed_by
        staff_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            staff_user.set_password('admin')
            staff_user.save()
        
        # Create the payment
        end_date = timezone.localtime().date()
        start_date = end_date - timedelta(days=7)
        
        payment = Payment.objects.create(
            farmer=farmer,
            amount=Decimal('1000.00'),
            start_date=start_date,
            end_date=end_date,
            payment_method=payment_method,
            status='completed',
            processed_by=staff_user,
            transaction_id=f'PAY-{farmer.id}-{int(timezone.now().timestamp())}'
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created payment: ID={payment.id}, '
                f'Farmer={payment.farmer}, '
                f'Amount={payment.amount}, '
                f'Transaction ID={payment.transaction_id}'
            )
        ) 