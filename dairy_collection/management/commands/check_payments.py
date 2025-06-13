from django.core.management.base import BaseCommand
from dairy_collection.models import Payment

class Command(BaseCommand):
    help = 'Check payments and their transaction IDs'

    def handle(self, *args, **options):
        payments = Payment.objects.all()
        self.stdout.write(f"Total payments: {payments.count()}")
        
        for payment in payments:
            self.stdout.write(
                f"Payment ID: {payment.id}, "
                f"Farmer: {payment.farmer}, "
                f"Amount: {payment.amount}, "
                f"Status: {payment.status}, "
                f"Transaction ID: {payment.transaction_id}"
            ) 