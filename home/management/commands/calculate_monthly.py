from django.core.management.base import BaseCommand
from home.models import MonthlyCalculation
from django.contrib import messages

class Command(BaseCommand):
    help = 'Calculate monthly data for all months of a selected year'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, help='Year for which to calculate data')

    def handle(self, *args, **kwargs):
        year = kwargs['year']

        for month in range(1, 13):
            # Get or create the MonthlyCalculation object for each month
            monthly_calculation, created = MonthlyCalculation.objects.get_or_create(year=year, month=month)
            monthly_calculation.update_calculations()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated calculations for {year}-{month}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully updated calculations for all months of {year}.'))
