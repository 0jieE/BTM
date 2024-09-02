import os
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from django.utils.html import format_html
from datetime import datetime as dt, timedelta
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, Count, Case, When, Q
from decimal import Decimal
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin

logger = logging.getLogger(__name__)

class User (AbstractUser,PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    extension_name = models.CharField(max_length=50, null=True, blank=True)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    def __str__(self):
        template = '{0.first_name} {0.middle_name} {0.last_name}'
        return template.format(self)
    
# ---------------------------------------------------------------------------------------------------------
# ------------------staff user---------------------------------------------------------------------

class Staff_manager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset( *args, **kwargs)
        return results.filter(staff = True)
    
class Staff_user(User):
    user = Staff_manager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.is_staff = True
            self.is_active = True
            self.is_superuser = False
            self.staff = True
            self.admin = False
            return super().save(*args, **kwargs)

    def welcome(self):
        return "Only for staff user"
    
class Admin_manager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset( *args, **kwargs)
        return results.filter(admin = True)
    
class Admin_user(User):
    user = Admin_manager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.is_staff = True
            self.is_active = True
            self.is_superuser = False
            self.staff = False
            self.admin = True
            return super().save(*args, **kwargs)

    def welcome(self):
        return "Only for admin user"

def get_upload_to(instance, filename):
    return os.path.join(f'business_{instance.business.business_no}', filename)

class PaymentMode(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

class BusinessType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

class ApplicationMethod(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

class Business(models.Model):
    business_no = models.CharField(max_length=100)  # Removed unique=True
    business_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    extension_name = models.CharField(max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    application_date = models.DateField()
    application_type = models.CharField(max_length=100)
    capital_investment = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    gross_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    payment_mode = models.ForeignKey('PaymentMode', on_delete=models.CASCADE)
    business_type = models.ForeignKey('BusinessType', on_delete=models.CASCADE)
    business_nature = models.CharField(max_length=255)
    application_method = models.ForeignKey('ApplicationMethod', on_delete=models.CASCADE)
    plate_no = models.CharField(max_length=100)
    date_issued = models.DateField(blank=True, null=True)
    telephone_no = models.CharField(max_length=15, blank=True, null=True)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"{self.business_no} - {self.business_name}"

    def get_picture_urls(self):
        return [picture.picture.url for picture in self.picture_set.all()]

    def get_picture_html(self):
        picture_urls = self.get_picture_urls()
        if not picture_urls:
            return ""
        picture_html = ''.join([format_html('<img src="{}" style="width:100%;" />', url) for url in picture_urls])
        return picture_html

    def has_paid(self, year_filter_int, month_filter_int=None):
        if year_filter_int is None:
            return False

        # Fetch collections associated with the business for the specified year
        collections = self.collection_set.filter(date_time__year=year_filter_int)
        collection_dates = list(collections.values_list('date_time', flat=True))

        payment_mode = self.payment_mode.name.lower()

        if payment_mode == 'annual':
            # Annual: Any collection within the year is sufficient
            return bool(collection_dates)

        elif payment_mode == 'bi-annual':
            # Bi-annual: Check if payments exist in the relevant half-year period
            if month_filter_int:
                if month_filter_int <= 6:
                    relevant_months = range(1, 7)
                else:
                    relevant_months = range(7, 13)
            else:
                relevant_months = range(1, 13)  # Consider the whole year if no month is specified

            return any(date.month in relevant_months for date in collection_dates)

        elif payment_mode == 'quarterly':
            # Quarterly: Determine relevant months in the quarter
            if month_filter_int:
                if month_filter_int <= 3:
                    relevant_months = range(1, 4)
                elif month_filter_int <= 6:
                    relevant_months = range(4, 7)
                elif month_filter_int <= 9:
                    relevant_months = range(7, 10)
                else:
                    relevant_months = range(10, 13)
            else:
                relevant_months = range(1, 13)  # Consider the whole year if no month is specified

            return any(date.month in relevant_months for date in collection_dates)

        return False



class BusinessYear(models.Model):
    business = models.ForeignKey(Business, related_name='years', on_delete=models.CASCADE)
    year = models.PositiveIntegerField()

    class Meta:
        unique_together = ('business', 'year')  # Ensures a business can only have one entry per year

    def __str__(self):
        return f"{self.business.business_name} - {self.year}"

class Picture(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=get_upload_to)

    def __str__(self):
        return f"Picture for {self.business.business_name}"

class Collection(models.Model):
    date_time = models.DateTimeField()
    or_no = models.CharField(max_length=20, unique=True)
    business_no = models.CharField(max_length=100)  # Change to CharField
    business_name = models.CharField(max_length=255)  # Added business_name for linking
    payor = models.CharField(max_length=255)
    business_tax = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    permit = models.CharField(max_length=100, blank=True, null=True)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    linked_business = models.ForeignKey(Business, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.business_no} - {self.or_no}"


class MonthlyCalculation(models.Model):
    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    paid_count = models.IntegerField(default=0)
    not_paid_count = models.IntegerField(default=0)
    annual_paid_count = models.IntegerField(default=0)
    bi_annual_paid_count = models.IntegerField(default=0)
    quarterly_paid_count = models.IntegerField(default=0)

    # payment_modes_count
    annual_count = models.IntegerField(default=0)
    bi_annual_count = models.IntegerField(default=0)
    quarterly_count = models.IntegerField(default=0)

    # monthly_totals/collections_per_mode
    total_collection = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    annual_collection = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    bi_annual_collection = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    quarterly_collection = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('year', 'month')

    def update_calculations(self):
        filters = {'collection__date_time__year': self.year, 'collection__date_time__month': self.month}
        businesses = Business.objects.annotate(
            total_collection=Sum('collection__total', filter=Q(**filters))
        )

        self.total_collection = businesses.aggregate(total=Sum('total_collection'))['total'] or Decimal('0.00')

        self.annual_collection = businesses.filter(payment_mode__name='Annual').aggregate(
            total=Sum('total_collection'))['total'] or Decimal('0.00')
        self.quarterly_collection = businesses.filter(payment_mode__name='Quarterly').aggregate(
            total=Sum('total_collection'))['total'] or Decimal('0.00')
        self.bi_annual_collection = businesses.filter(payment_mode__name='Bi-Annual').aggregate(
            total=Sum('total_collection'))['total'] or Decimal('0.00')

        paid_count = 0
        not_paid_count = 0
        annual_paid = 0
        quarterly_paid = 0
        bi_annual_paid = 0

        annual_count = 0
        quarterly_count = 0
        bi_annual_count = 0

        for business in businesses:
            payment_mode = business.payment_mode.name

            if payment_mode == 'Annual':
                annual_count += 1
            elif payment_mode == 'Quarterly':
                quarterly_count += 1
            elif payment_mode == 'Bi-Annual':
                bi_annual_count += 1

            if business.has_paid(self.year, self.month):
                paid_count += 1
                if payment_mode == 'Annual':
                    annual_paid += 1
                elif payment_mode == 'Quarterly':
                    quarterly_paid += 1
                elif payment_mode == 'Bi-Annual':
                    bi_annual_paid += 1
            else:
                not_paid_count += 1

        self.paid_count = paid_count
        self.not_paid_count = not_paid_count
        self.annual_paid_count = annual_paid
        self.quarterly_paid_count = quarterly_paid
        self.bi_annual_paid_count = bi_annual_paid

        self.annual_count = annual_count
        self.quarterly_count = quarterly_count
        self.bi_annual_count = bi_annual_count

        self.save()

    def __str__(self):
        return f"Calculations for {self.year}-{self.month}"


class YearlyCalculation(models.Model):
    year = models.PositiveIntegerField()
    total_businesses = models.IntegerField(default=0)
    total_collection = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    annual_collection = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    bi_annual_collection = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    quarterly_collection = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))

    def update_calculations(self):
        monthly_data = MonthlyCalculation.objects.filter(year=self.year).aggregate(
            total_collection=Sum('total_collection') or Decimal('0.00'),
            annual_collection=Sum('annual_collection') or Decimal('0.00'),
            bi_annual_collection=Sum('bi_annual_collection') or Decimal('0.00'),
            quarterly_collection=Sum('quarterly_collection') or Decimal('0.00')
        )
        self.total_collection = monthly_data['total_collection'] or Decimal('0.00')
        self.annual_collection = monthly_data['annual_collection'] or Decimal('0.00')
        self.bi_annual_collection = monthly_data['bi_annual_collection'] or Decimal('0.00')
        self.quarterly_collection = monthly_data['quarterly_collection'] or Decimal('0.00')
        self.total_businesses = Business.objects.count()
        self.save()

    def __str__(self):
        return f"Yearly Calculations for {self.year}"


class UserLogs(models.Model):
    user = models.ForeignKey(Staff_user, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    pictures = models.ManyToManyField('Picture', blank=True)

    def __str__(self):
        return f"Log by {self.user.username} on {self.timestamp}"
