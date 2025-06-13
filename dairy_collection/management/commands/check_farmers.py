from django.core.management.base import BaseCommand
from dairy_collection.models import Farmer

class Command(BaseCommand):
    help = 'Check farmers in the database'

    def handle(self, *args, **options):
        farmers = Farmer.objects.all()
        self.stdout.write(f"Total farmers: {farmers.count()}")
        
        for farmer in farmers:
            self.stdout.write(
                f"Farmer ID: {farmer.id}, "
                f"Name: {farmer.user.first_name} {farmer.user.last_name}, "
                f"Phone: {farmer.phone_number}"
            ) 