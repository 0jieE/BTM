from django.core.management.base import BaseCommand
from home.models import YearlyCalculation

class Command(BaseCommand):
    help = 'Calculate yearly data for the specified year'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, help='Year for which to calculate data')

    def handle(self, *args, **kwargs):
        year = kwargs['year']
        yearly_calculation, created = YearlyCalculation.objects.get_or_create(year=year)
        yearly_calculation.update_calculations()
        self.stdout.write(self.style.SUCCESS(f'Successfully updated yearly calculations for {year}'))
