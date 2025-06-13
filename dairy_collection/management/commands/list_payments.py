from django.core.management.base import BaseCommand
from dairy_collection.models import Payment

class Command(BaseCommand):
    help = 'List all payments in detail'

    def handle(self, *args, **options):
        payments = Payment.objects.select_related('farmer', 'payment_method').all()
        
        if not payments.exists():
            self.stdout.write(self.style.WARNING('No payments found in the database'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {payments.count()} payments:'))
        for payment in payments:
            self.stdout.write(
                f'\nPayment Details:\n'
                f'- ID: {payment.id}\n'
                f'- Farmer: {payment.farmer}\n'
                f'- Amount: ₹{payment.amount}\n'
                f'- Status: {payment.status}\n'
                f'- Transaction ID: {payment.transaction_id}\n'
                f'- Payment Method: {payment.payment_method}\n'
                f'- Period: {payment.start_date} to {payment.end_date}\n'
                f'- Created At: {payment.created_at}'
            ) 