from django.core.management.base import BaseCommand
from dairy_collection.models import Payment, MilkCollection

class Command(BaseCommand):
    help = 'Clean up test payments from the database'

    def handle(self, *args, **options):
        # Delete all payments
        payments = Payment.objects.all()
        count = payments.count()
        payments.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} test payments')
        ) 

        # Get the latest completed payment for this farmer
        latest_payment = Payment.objects.filter(
            farmer=farmer,
            status='completed'
        ).order_by('-end_date').first()

        if latest_payment:
            # Only include collections after the last payment's end date
            collections = MilkCollection.objects.filter(
                farmer=farmer,
                date__date__gt=latest_payment.end_date
            )
        else:
            # If no payments exist, include all collections
            collections = MilkCollection.objects.filter(farmer=farmer) 