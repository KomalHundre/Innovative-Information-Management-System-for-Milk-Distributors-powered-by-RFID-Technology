from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
from dairy_collection.models import Payment, Farmer, PaymentMethod
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a test payment with robust error handling'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get the first farmer
                try:
                    farmer = Farmer.objects.first()
                    if not farmer:
                        self.stdout.write(self.style.ERROR('No farmers found in the database'))
                        return
                    self.stdout.write(f'Found farmer: {farmer}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error getting farmer: {str(e)}'))
                    return

                # Get or create payment method
                try:
                    payment_method, created = PaymentMethod.objects.get_or_create(
                        name='Bank Transfer',
                        defaults={'is_active': True}
                    )
                    self.stdout.write(f'{"Created" if created else "Found"} payment method: {payment_method}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error with payment method: {str(e)}'))
                    return

                # Create the payment
                try:
                    end_date = timezone.localtime().date()
                    start_date = end_date - timedelta(days=7)
                    transaction_id = f'PAY-{farmer.id}-{int(timezone.now().timestamp())}'

                    payment = Payment.objects.create(
                        farmer=farmer,
                        amount=Decimal('1000.00'),
                        start_date=start_date,
                        end_date=end_date,
                        payment_method=payment_method,
                        status='completed',
                        transaction_id=transaction_id
                    )

                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully created payment:\n'
                        f'- ID: {payment.id}\n'
                        f'- Farmer: {payment.farmer}\n'
                        f'- Amount: {payment.amount}\n'
                        f'- Transaction ID: {payment.transaction_id}\n'
                        f'- Status: {payment.status}'
                    ))

                    # Verify the payment was created
                    verification = Payment.objects.get(id=payment.id)
                    self.stdout.write(self.style.SUCCESS(
                        f'Verified payment exists:\n'
                        f'- ID: {verification.id}\n'
                        f'- Transaction ID: {verification.transaction_id}'
                    ))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating payment: {str(e)}'))
                    raise

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Transaction failed: {str(e)}')) 