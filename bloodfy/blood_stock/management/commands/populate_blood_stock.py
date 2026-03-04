"""
Management command to populate sample blood stock data.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from blood_stock.models import BloodStock
import random


class Command(BaseCommand):
    help = 'Populate database with sample blood stock data'

    def handle(self, *args, **kwargs):
        # Clear existing blood stock
        BloodStock.objects.all().delete()
        self.stdout.write('Cleared existing blood stock data')

        # Blood groups
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        
        # Hospitals
        hospitals = [
            ('Jinnah Hospital', 'Lahore'),
            ('Services Hospital', 'Lahore'),
            ('Mayo Hospital', 'Lahore'),
            ('Shaukat Khanum Memorial Hospital', 'Lahore'),
            ('National Hospital', 'Lahore'),
            ('Aga Khan University Hospital', 'Karachi'),
            ('Civil Hospital', 'Karachi'),
        ]

        stock_entries = []
        
        for hospital_name, city in hospitals:
            for blood_group in blood_groups:
                # Random units between 10-100
                units = random.randint(10, 100)
                
                # Determine thresholds
                critical = 5
                minimum = 15
                
                stock = BloodStock(
                    blood_group=blood_group,
                    units_available=units,
                    hospital_name=hospital_name,
                    hospital_city=city,
                    hospital_address=f'{hospital_name} Address, {city}',
                    contact_number=f'+92-300-{random.randint(1000000, 9999999)}',
                    minimum_threshold=minimum,
                    critical_threshold=critical,
                )
                stock_entries.append(stock)

        # Bulk create
        BloodStock.objects.bulk_create(stock_entries)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(stock_entries)} blood stock entries'
            )
        )
        
        # Display summary
        self.stdout.write('\nStock Summary by Blood Group:')
        for blood_group in blood_groups:
            total_units = BloodStock.objects.filter(
                blood_group=blood_group
            ).aggregate(total=models.Sum('units_available'))['total'] or 0
            
            self.stdout.write(f'  {blood_group}: {total_units} units across all hospitals')
            
        self.stdout.write('\nDone!')
