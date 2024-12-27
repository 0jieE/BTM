import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
import folium
from django.views import View
from .forms import *
from .models import *
from datetime import datetime 
import logging
from django.utils import timezone
from django.utils.timezone import make_aware
import pytz
from django.db.models.functions import ExtractYear, ExtractMonth
from datetime import date, timedelta, datetime as dt
from .forms import MultiplePictureForm
from django.core.serializers.json import DjangoJSONEncoder
import json
from folium.plugins import Geocoder
from django.db.models import Sum, Count
from decimal import Decimal
from django.db.models import Sum, Count, Case, When, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.db import models
from django.contrib import messages
from django.contrib.auth import logout, authenticate,login
import calendar
from django.utils.timezone import now
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def index(request):
    return redirect('/login')

def user_logout(request):
  logout(request)
  return redirect('/login')

def user_login(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('/admin')
            elif user is not None and not user.is_superuser:
                login(request, user)
                return redirect('map-view')
            else:
                msg= 'invalid credentials'
        else:
            msg = 'error validating form'
    return render(request, 'accounts/login.html', {'form': form, 'msg': msg})



def staff_register(request):
    msg = None
    success = False
    if request.method == "POST":
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            return redirect("login")

        else:
            msg = 'Form is not valid'
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'accounts/register.html',{"form": form, "msg": msg, "success": success})


def admin_register(request):
    msg = None
    success = False
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            return redirect("login")

        else:
            msg = 'Form is not valid'
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'accounts/register.html',{"form": form, "msg": msg, "success": success})



def map_view(request):
    search_query = request.GET.get('search', '')
    year_filter = request.GET.get('year', None)
    month_filter = request.GET.get('month', None)
    year_filter_int = int(year_filter) if year_filter else None
    month_filter_int = int(month_filter) if month_filter else None

    businesses_with_location = Business.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

    if search_query:
        businesses_with_location = businesses_with_location.filter(business_name__icontains=search_query)

    if year_filter:
        businesses_with_location = businesses_with_location.filter(years__year=year_filter).distinct()

    businesses_data = []
    for business in businesses_with_location:
        paid_status = business.has_paid(year_filter_int, month_filter_int)

        owner_name = f"{business.first_name or ''} {business.middle_name or ''} {business.last_name or ''}".strip()


        businesses_data.append({
            'id': business.id,
            'name': business.business_name,
            'owner': owner_name,
            'mobile_no': business.mobile_no,
            'telephone_no': business.telephone_no,
            'location': business.location,
            'capital_investment': business.capital_investment,
            'gross_sales': business.gross_sales,
            'business_nature': business.business_nature,
            'latitude': business.latitude,
            'longitude': business.longitude,
            'payment_mode': business.payment_mode.name,
            'paid': paid_status,
            'picture_html': business.get_picture_html(),
            "directions_link": f"https://maps.google.com/?q={business.latitude},{business.longitude}" if business.latitude and business.longitude else None,
            "save_link": "#",
            "share_link": "#",
        })

        

    all_years = BusinessYear.objects.values_list('year', flat=True).distinct().order_by('year')
    months = [(i, dt(2000, i, 1).strftime('%B')) for i in range(1, 13)]

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(businesses_data, safe=False)

    context = {
        'businesses_json': json.dumps(businesses_data, cls=DjangoJSONEncoder),
        'business_years': all_years,
        'months': months,
    }
    
    return render(request, 'maps/map_script.html', context)


def monthly_calculation(request):
    year_filter = request.GET.get('year')
    month_filter = request.GET.get('month')
    
    monthly_calculation_data = []
    yearly_calculation_data = {}

    if year_filter:

        yearly_calculation = YearlyCalculation.objects.filter(year=year_filter).first()

        if yearly_calculation:
            yearly_calculation_data = {
                'year': yearly_calculation.year,
                'yearly_total_businesses': yearly_calculation.total_businesses,
                'yearly_total_collection': str(yearly_calculation.total_collection),
                'yearly_annual_collection': str(yearly_calculation.annual_collection),
                'yearly_bi_annual_collection': str(yearly_calculation.bi_annual_collection),
                'yearly_quarterly_collection': str(yearly_calculation.quarterly_collection),
            }
        
        # Fetch data for the entire year
        monthly_calculations = MonthlyCalculation.objects.filter(year=year_filter).order_by('month')

        # Create a list of dictionaries for each month in the year (1-12)
        for month in range(1, 13):
            # Try to find data for the current month in the loop
            calculation = monthly_calculations.filter(month=month).first()
            if calculation:
                # If data exists for the month, add it to the response
                monthly_calculation_data.append({
                    'month': month,
                    'paid_count': calculation.paid_count,
                    'not_paid_count': calculation.not_paid_count,
                    'annual_paid_count': calculation.annual_paid_count,
                    'bi_annual_paid_count': calculation.bi_annual_paid_count,
                    'quarterly_paid_count': calculation.quarterly_paid_count,
                    'annual_count': calculation.annual_count,
                    'bi_annual_count': calculation.bi_annual_count,
                    'quarterly_count': calculation.quarterly_count,
                    'total_collection': str(calculation.total_collection),
                    'annual_collection': str(calculation.annual_collection),
                    'bi_annual_collection': str(calculation.bi_annual_collection),
                    'quarterly_collection': str(calculation.quarterly_collection),
                })
            else:
                # If no data exists for the month, add a zeroed entry for that month
                monthly_calculation_data.append({
                    'month': month,
                    'paid_count': 0,
                    'not_paid_count': 0,
                    'annual_paid_count': 0,
                    'bi_annual_paid_count': 0,
                    'quarterly_paid_count': 0,
                    'annual_count': 0,
                    'bi_annual_count': 0,
                    'quarterly_count': 0,
                    'total_collection': '0.00',
                    'annual_collection': '0.00',
                    'bi_annual_collection': '0.00',
                    'quarterly_collection': '0.00',
                })

        # If a specific month is selected, filter the data for the summary
        if month_filter:
            selected_month_data = next((item for item in monthly_calculation_data if item['month'] == int(month_filter)), None)
            return JsonResponse({'monthly_calculation': monthly_calculation_data, 'selected_month': selected_month_data}, safe=False)

    return JsonResponse({
        'monthly_calculation': monthly_calculation_data,
        'yearly_calculation': yearly_calculation_data,
    }, safe=False)


def process_data_to_calculate(request):
    form = YearSelectionForm(request.POST)
    if form.is_valid():
        year = form.cleaned_data['year']

        # Monthly calculations
        for month in range(1, 13):  # Loop through all 12 months
            monthly_calculation, created = MonthlyCalculation.objects.get_or_create(year=year, month=month)
            monthly_calculation.update_calculations()
            messages.success(request, f'Successfully updated calculations for {year}-{month}')

        # Yearly calculation
        yearly_calculation, created = YearlyCalculation.objects.get_or_create(year=year)
        yearly_calculation.update_calculations()
        messages.success(request, f'Successfully updated yearly calculations for {year}')
        
        return JsonResponse({
            'form_is_valid': True,
        })
    else:
        logger.error("Form is not valid")
        return JsonResponse({'form_is_valid': False})


def calculate_data(request):
    if request.method == 'POST':
        return process_data_to_calculate(request)
    else:
        form = YearSelectionForm()
        context = {'form': form}
        return JsonResponse({
            'html_form': render_to_string('maps/calculate_data.html', context, request=request)
        })




def business(request):
    selected_year = int(request.GET.get('year', dt.now().year))
    selected_business_id = request.GET.get('business_id')

    businesses = Business.objects.filter(years__year=selected_year).distinct()
    years = BusinessYear.objects.values_list('year', flat=True).distinct().order_by('year')

    if not selected_business_id and businesses.exists():
        selected_business = businesses.first()
    else:
        selected_business = businesses.filter(id=selected_business_id).first()

    pictures = Picture.objects.filter(business=selected_business) if selected_business else []

    collections_by_year = {}
    if selected_business:
        collections = Collection.objects.filter(linked_business=selected_business).annotate(
            collection_year=ExtractYear('date_time')
        )
        for collection in collections:
            year = collection.collection_year
            if year not in collections_by_year:
                collections_by_year[year] = []
            collections_by_year[year].append(collection)

    # Default location and zoom
    map_location = [7.188428, 124.545665]
    zoom_start = 15
    location_message = ""

    # Create a Folium map
    if selected_business and selected_business.latitude and selected_business.longitude:
        lat = float(selected_business.latitude)
        lon = float(selected_business.longitude)
        map_location = [lat, lon]
        zoom_start = 17
    else:
        location_message = "This business has no location yet."

    m = folium.Map(location=map_location, zoom_start=zoom_start)

    # Add a marker for the selected business
    if selected_business and selected_business.latitude and selected_business.longitude:
        folium.Marker(
            location=[lat, lon],
            popup=f'{selected_business.business_name} ({selected_business.business_no})',
            tooltip=selected_business.business_name
        ).add_to(m)

    # Convert the map to an HTML string
    map_html = m._repr_html_()

    context = {
        'segment': 'business',
        'businesses': businesses,
        'years': years,
        'selected_year': selected_year,
        'selected_business': selected_business,
        'pictures': pictures,
        'map_html': map_html,  # Pass the map HTML to the template
        'location_message': location_message,  # Pass the location message to the template
        'collections_by_year': collections_by_year,  # Pass collections grouped by year
    }

    return render(request, 'business/business.html', context)








#User logs///////////////////////////////////////////////////////////

def edit_location(request, pk):
    data = dict()
    business = get_object_or_404(Business, pk=pk)

    if request.method == 'POST':
        form = EditLocationForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            # Create a log entry
            UserLogs.objects.create(
                user=request.user,
                business=business,
                latitude=business.latitude,
                longitude=business.longitude,
                action=f"Updated location to latitude: {business.latitude}, longitude: {business.longitude}"
            )
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = EditLocationForm(instance=business)
    
    context = {'form': form}
    data['html_form'] = render_to_string('business/edit_location.html', context, request=request)
    return JsonResponse(data)

def location(request, pk):
    business = get_object_or_404(Business, pk=pk)
    if request.method == 'POST':
        form = EditLocationForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            UserLogs.objects.create(
                user=request.user,
                business=business,
                latitude=business.latitude,
                longitude=business.longitude,
                action=f"Updated location to latitude: {business.latitude}, longitude: {business.longitude}"
            )
            return redirect("business")
    else:
        form = EditLocationForm(instance=business)

    context = {'form': form}
    return render(request, 'business/location.html', context)


def upload_pictures(request):
    data = dict()
    
    if request.method == 'POST':
        business_id = request.POST.get('business_no')
    else:
        business_id = request.GET.get('business_id')

    business = get_object_or_404(Business, id=business_id)
    
    if request.method == 'POST':
        form = MultiplePictureForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('pictures')
            picture_objects = []
            for f in files:
                picture = Picture.objects.create(business=business, business_name=business.business_name, picture=f)
                picture_objects.append(picture)
            # Create a log entry with pictures
            log = UserLogs.objects.create(
                user=request.user,
                business=business,
                action=f"Uploaded {len(files)} pictures"
            )
            log.pictures.set(picture_objects)  # Link pictures to the log
            log.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = MultiplePictureForm(initial={'business_no': business.id})

    context = {'form': form}
    data['html_form'] = render_to_string('business/upload_photos.html', context, request=request)
    return JsonResponse(data)




def user_logs_view(request):
    users = User.objects.all()
    current_date = dt.now()
    selected_year = int(request.GET.get('year', current_date.year))
    selected_month = int(request.GET.get('month', current_date.month))
    selected_day = int(request.GET.get('day', current_date.day))
    selected_user_id = request.GET.get('user_id', users.first().id)
    if not selected_user_id and users.exists():
        selected_user = users.first()
    else:
        selected_user = users.filter(id=selected_user_id).first()

    print(f"{selected_year}")
    # Filter logs based on selected filters
    logs = UserLogs.objects.filter(user=selected_user)
    logs = logs.filter(timestamp__year=selected_year, timestamp__month=selected_month, timestamp__day=selected_day)

    # Create a Folium map centered on a default location
    map_center = [0, 0]  # Default center of the map
    if logs.filter(latitude__isnull=False, longitude__isnull=False).exists():
        first_log_with_coords = logs.filter(latitude__isnull=False, longitude__isnull=False).first()
        map_center = [first_log_with_coords.latitude, first_log_with_coords.longitude]
    folium_map = folium.Map(location=map_center, zoom_start=15)

    # Add markers for logs with coordinates
    for log in logs.filter(latitude__isnull=False, longitude__isnull=False):
        folium.Marker(
            location=[log.latitude, log.longitude],
            popup=f"{log.action} at {log.business}",
        ).add_to(folium_map)

    # Render the map to HTML
    map_html = folium_map._repr_html_()

    # Get the range of years starting from 2020 to current year
    years = range(2020, current_date.year + 1)
    months = [{'num': i, 'name': current_date.replace(month=i).strftime('%B')} for i in range(1, 13)]
    
    # Dynamically calculate the number of days in the selected month
    days_in_month = dt(selected_year, selected_month, 1) + timedelta(days=31)
    days = range(1, (days_in_month - timedelta(days=days_in_month.day)).day + 1)

    context = {
        'users': users,
        'selected_user': selected_user,
        'logs': logs,
        'years': years,
        'months': months,
        'days': days,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_day': selected_day,
        'map_html': map_html,  # Pass the map HTML to the context
    }

    return render(request, 'logs/user_logs.html', context)


def get_user_logs(request, user_id):
    logs = UserLogs.objects.filter(user_id=user_id)
    logs_data = []
    for log in logs:
        pictures = [picture.picture.url for picture in log.pictures.all()]
        logs_data.append({
            'action': log.action,
            'timestamp': log.timestamp,
            'business': log.business.business_name,
            'pictures': pictures
        })
    return JsonResponse({'logs': logs_data})



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response



def logs_report_pdf(request):
    users = User.objects.all()
    selected_year = int(request.GET.get('year'))
    selected_month = int(request.GET.get('month'))
    selected_day = int(request.GET.get('day'))
    selected_user_id = int(request.GET.get('user_id'))

    # Use get() instead of filter() to retrieve a single user
    selected_user = users.get(id=selected_user_id)

    # Filter logs by selected user and date
    logs = UserLogs.objects.filter(
        user=selected_user,
        timestamp__year=selected_year,
        timestamp__month=selected_month,
        timestamp__day=selected_day
    )

    # Log the number of logs found
    print(f"Found {logs.count()} logs for user {selected_user} on {selected_year}-{selected_month}-{selected_day}")

    context = {
        'logs': logs,
        'user': selected_user,
        'year': selected_year,
        'month': selected_month,
        'day': selected_day,
    }

    return render_to_pdf('logs/logs_report.html', context)





def collection(request):

    collections = Collection.objects.all()

    context = {
        'collections': collections,
    }

    return render(request, 'collection/collection.html', context)


def business_table(request):
    businesses = Business.objects.all()
    
    businesses_with_years = []
    for business in businesses:
        business_years = BusinessYear.objects.filter(business=business).values_list('year', flat=True)
        businesses_with_years.append({
            'business': business,
            'years': list(business_years)
        })

    context = {
        'business_table': 'business_table',
        'businesses_with_years': businesses_with_years,
    }

    return render(request, 'business/business_table.html', context)



logger = logging.getLogger(__name__)

def process_business_file(file):
    df = pd.read_excel(file)
    skipped_rows = []
    duplicate_groups = {}

    def parse_datetime(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                logger.error(f"Invalid date format: {date_str}")
                return None  # Return None if the date format is invalid

    # Detect duplicates within the file based on business_no and year
    duplicates = df[df.duplicated(['business_no', 'year'], keep=False)]

    # Debug statement to check dataframe content
    logger.debug("Dataframe content:\n%s", df.to_string())

    for index, row in df.iterrows():
        business_no = row['business_no']
        business_name = row['business_name']
        year = int(row['year'])  # Use the year column directly
        row_number = index + 2  # Adjust the row number by adding 2 to account for the header and 0-based index

        logger.debug("Processing row %d: business_no=%s, business_name=%s, year=%d", row_number, business_no, business_name, year)

        if (business_no, year) in duplicates[['business_no', 'year']].values:
            if business_no not in duplicate_groups:
                duplicate_groups[business_no] = []
            duplicate_groups[business_no].append(row_number)

        try:
            payment_mode, _ = PaymentMode.objects.get_or_create(name=row['payment_mode'])
            business_type, _ = BusinessType.objects.get_or_create(name=row['business_type'])
            application_method, _ = ApplicationMethod.objects.get_or_create(name=row['application_method'])

            contact_no = row['contact_no'].split(',')
            telephone_no = contact_no[0].strip() if contact_no[0].strip() != 'N/A' else None
            mobile_no = contact_no[1].strip() if len(contact_no) > 1 else None

            # Convert dates to the correct format
            application_date = parse_datetime(row['application_date'])
            if application_date:
                application_date = make_aware(application_date, pytz.timezone('UTC'))

            date_issued = None
            if not pd.isna(row.get('date_issued')):
                date_issued = parse_datetime(row['date_issued'])
                if date_issued:
                    date_issued = make_aware(date_issued, pytz.timezone('UTC'))

            # Handle gender value, default to 'N/A' if not valid
            gender = None
            if not pd.isna(row['gender']):
                gender = str(row['gender']).strip()
            if gender not in ['Male', 'Female']:
                gender = 'N/A'  # Ensure gender is never None

            if application_date is None:
                logger.error(f"Skipping row {row_number} due to invalid application_date: {row['application_date']}")
                skipped_rows.append(row_number)
                continue

            # Handle NaN values for decimal fields
            capital_investment = 0.00 if pd.isna(row['capital_investment']) else float(row['capital_investment'])
            gross_sales = 0.00 if pd.isna(row['gross_sales']) else float(row['gross_sales'])

            # Check for duplicate BusinessYear based on business_no and year
            existing_business_year = BusinessYear.objects.filter(business__business_no=business_no, year=year).first()
            if existing_business_year:
                # If business names don't match, skip the row
                if existing_business_year.business.business_name != business_name:
                    logger.error(f"Skipping row {row_number} due to name conflict for business_no: {business_no} and year: {year}")
                    skipped_rows.append(row_number)
                    continue

            # Check if a business with the same business_no and business_name already exists
            existing_business = Business.objects.filter(business_no=business_no, business_name=business_name).first()
            if existing_business:
                # Update the existing business record
                business, created = Business.objects.update_or_create(
                    business_no=business_no,
                    business_name=business_name,
                    defaults={
                        'last_name': row['last_name'],
                        'first_name': row['first_name'],
                        'middle_name': row.get('middle_name'),
                        'extension_name': row.get('extension_name'),
                        'gender': gender,
                        'location': row['location'],
                        'application_date': application_date,
                        'application_type': row['application_type'],
                        'capital_investment': capital_investment,
                        'gross_sales': gross_sales,
                        'payment_mode': payment_mode,
                        'business_type': business_type,
                        'business_nature': row['business_nature'],
                        'application_method': application_method,
                        'plate_no': row.get('plate_no'),
                        'date_issued': date_issued,
                        'telephone_no': telephone_no,
                        'mobile_no': mobile_no,
                        'latitude': None if pd.isna(row.get('latitude')) else row['latitude'],
                        'longitude': None if pd.isna(row.get('longitude')) else row['longitude'],
                    }
                )
            else:
                # Create a new business record
                business = Business.objects.create(
                    business_no=business_no,
                    business_name=business_name,
                    last_name=row['last_name'],
                    first_name=row['first_name'],
                    middle_name=row.get('middle_name'),
                    extension_name=row.get('extension_name'),
                    gender=gender,
                    location=row['location'],
                    application_date=application_date,
                    application_type=row['application_type'],
                    capital_investment=capital_investment,
                    gross_sales=gross_sales,
                    payment_mode=payment_mode,
                    business_type=business_type,
                    business_nature=row['business_nature'],
                    application_method=application_method,
                    plate_no=row.get('plate_no'),
                    date_issued=date_issued,
                    telephone_no=telephone_no,
                    mobile_no=mobile_no,
                    latitude=None if pd.isna(row.get('latitude')) else row['latitude'],
                    longitude=None if pd.isna(row.get('longitude')) else row['longitude'],
                )

            # Check if a BusinessYear record already exists
            business_year_exists = BusinessYear.objects.filter(business=business, year=year).exists()
            if not business_year_exists:
                BusinessYear.objects.create(
                    business=business,
                    year=year,
                )

            logger.info(f"Processed row {row_number}: {business_no} for year {year}")

        except Exception as e:
            logger.error(f"Error processing row {row_number}: {e}")
            skipped_rows.append(row_number)

    # Filter out entries in duplicate_groups that do not have duplicates
    duplicate_groups = {key: value for key, value in duplicate_groups.items() if len(value) > 1}

    return skipped_rows, duplicate_groups


def process_business_upload(request):
    business_form = UploadBusinessFileForm(request.POST, request.FILES)
    if business_form.is_valid():
        skipped_rows, duplicate_groups = process_business_file(request.FILES['file'])
        return JsonResponse({
            'form_is_valid': True,
            'skipped_rows': skipped_rows,
            'duplicate_groups': duplicate_groups,
        })
    else:
        logger.error("Form is not valid")
        return JsonResponse({'form_is_valid': False})


def UploadBusinessFileView(request):
    if request.method == 'POST':
        return process_business_upload(request)
    else:
        business_form = UploadBusinessFileForm()
        context = {'business_form': business_form}
        return JsonResponse({
            'html_form': render_to_string('upload_business.html', context, request=request)
        })




def parse_datetime(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Invalid date format: {date_str}")
            return None

def process_collection_file(file):
    df = pd.read_excel(file)
    skipped_rows = []

    for index, row in df.iterrows():
        row_number = index + 2  # Adjust the row number by adding 2 to account for the header and 0-based index

        try:
            # Check if 'date' key exists in the row
            if 'date' not in row:
                logger.error(f"'date' key not found in row {row_number}")
                skipped_rows.append(row_number)
                continue
            
            # Convert date to the correct format
            date_time = parse_datetime(row['date'])
            if date_time:
                date_time = make_aware(date_time, pytz.timezone('Asia/Manila'))
            
            if date_time is None:
                logger.error(f"Skipping row {row_number} due to invalid date: {row['date']}")
                skipped_rows.append(row_number)
                continue

            business_no = row['business_no']
            business_name = row['business_name']
            linked_business = None
            try:
                linked_business = Business.objects.get(business_no=business_no, business_name=business_name)
                logger.debug(f"Found linked business for business_no {business_no} and business_name {business_name}")
            except Business.DoesNotExist:
                logger.warning(f"Business {business_no} with name {business_name} does not exist yet. It will be linked later if created.")

            # Handle NaN values for decimal fields
            business_tax = 0.00 if pd.isna(row['business_tax']) else float(row['business_tax'])
            total = 0.00 if pd.isna(row['total']) else float(row['total'])

            permit_value = '' if pd.isna(row.get('permit')) else row['permit'] 

            # Create or update the Collection record
            collection, created = Collection.objects.update_or_create(
                or_no=row['or_no'],
                defaults={
                    'date_time': date_time,
                    'business_no': business_no,
                    'business_name': business_name,
                    'payor': row['payor'],
                    'business_tax': business_tax,
                    'permit': permit_value,
                    'total': total,
                    'linked_business': linked_business,
                }
            )
            if created:
                logger.info(f"Created new row {row_number}: {row['or_no']}")
            else:
                # Add the total to the existing record
                collection.total += total
                collection.save()
                logger.info(f"Updated row {row_number} with new total: {row['or_no']}")

        except Exception as e:
            logger.error(f"Error processing row {row_number}: {e}")
            skipped_rows.append(row_number)

    return skipped_rows




def UploadCollectionFileView(request):
    data = dict()
    if request.method == 'POST':
        collection_form = UploadCollectionFileForm(request.POST, request.FILES)
        if collection_form.is_valid():
            skipped_rows = process_collection_file(request.FILES['file'])
            data['form_is_valid'] = True
            data['skipped_rows'] = skipped_rows
            logger.info(f"Collection file processed successfully with {len(skipped_rows)} skipped rows")
        else:
            logger.error("Form is not valid")
    else:
        collection_form = UploadCollectionFileForm()
    
    context = {'collection_form': collection_form}
    data['html_form'] = render_to_string('upload_collection.html', context, request=request)
    return JsonResponse(data)













def sms_view(request):
    years = BusinessYear.objects.values_list('year', flat=True).distinct()
    current_year = dt.now().year
    payment_modes = PaymentMode.objects.all()

    contact_id = request.GET.get('contact_id')
    selected_contact = None

    if contact_id and contact_id.isdigit():
        try:
            selected_contact = Business.objects.get(id=int(contact_id))
        except Business.DoesNotExist:
            selected_contact = None

    return render(request, 'sms/sms.html', {
        'years': years,
        'payment_modes': payment_modes,
        'current_year': current_year,
        'selected_contact': selected_contact,
    })


def get_contacts(request):

    is_message_all = request.GET.get('message_all') == 'true'

    if is_message_all:
        return JsonResponse({'is_message_all': True, 'contacts': []})

    selected_year = request.GET.get('year')
    selected_payment_mode = request.GET.get('payment_mode')
    paid_filter = request.GET.get('paid')

    year_filter_int = int(dt.now().year)
    month_filter_int = int(dt.now().month)

    contacts_query = Business.objects.all()

    if paid_filter == 'paid':
        contacts_query = contacts_query.filter(
            id__in=Business.objects.filter(
                id__in=[
                    contact.id for contact in contacts_query if contact.has_paid(year_filter_int, month_filter_int)
                ]
            ).values_list('id', flat=True)
        )
    elif paid_filter == 'unpaid':

        contacts_query = contacts_query.filter(
            id__in=Business.objects.filter(
                id__in=[
                    contact.id for contact in contacts_query if not contact.has_paid(year_filter_int, month_filter_int)
                ]
            ).values_list('id', flat=True)
        )

    if selected_year and selected_year.isdigit():
        contacts_query = contacts_query.filter(
            id__in=BusinessYear.objects.filter(year=int(selected_year)).values_list('business_id', flat=True)
        )

    if selected_payment_mode:
        contacts_query = contacts_query.filter(payment_mode__id=selected_payment_mode)

    contacts = [
        {
            'id': contact.id,
            'paid': contact.has_paid(year_filter_int, month_filter_int),
            'business_name': contact.business_name,
            'mobile_no': contact.mobile_no,
            'payment_mode': contact.payment_mode.name, 
        }
        for contact in contacts_query
    ]

    return JsonResponse({'is_message_all': False, 'contacts': contacts})



def get_messages(request):
    contact_id = request.GET.get('contact_id')
    if not contact_id or not contact_id.isdigit():
        return JsonResponse({'error': 'Invalid contact ID'}, status=400)

    contact = get_object_or_404(Business, id=int(contact_id))
    messages = AdminMessage.objects.filter(contact=contact).values('id', 'content', 'sender', 'sent_status')

    return JsonResponse({'messages': list(messages)})


@csrf_exempt
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

    data = json.loads(request.body)
    message = data.get('message')
    contact_id = data.get('contact_id')
    message_id = data.get('message_id')  
    filters = data.get('filters', {})

    if not message:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    def send_sms(mobile_no, message):
        """Function to send SMS using SIM800C."""
        try:
            import serial
            import time
            
            #ser = serial.Serial('COM5', 115200, timeout=5) #windows
            ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=5)  #linux
            time.sleep(2)

            ser.write('AT+CMGF=1\r\n'.encode())  
            time.sleep(1)
            ser.write(b'AT+CSMP=17,167,0,8\r\n') 
            time.sleep(1)

            ser.write('AT+CMGS="{}"\r\n'.format(mobile_no).encode())  
            time.sleep(1)
            ser.write(message.encode())  
            ser.write(bytes([26])) 
            time.sleep(3)

            ser.close()
            return True 
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False  

    if message_id:
        admin_message = get_object_or_404(AdminMessage, id=message_id)
        sent_status = send_sms(admin_message.contact.mobile_no, message)

        admin_message.sent_status = sent_status 
        admin_message.save(update_fields=['sent_status'])  

        return JsonResponse({
            'success': sent_status,
            'message': 'Message resent successfully!' if sent_status else 'Failed to resend message.',
            'message_id': admin_message.id,
            'sent_status': sent_status
        }, status=200 if sent_status else 500)

    if contact_id:
        contact = get_object_or_404(Business, id=int(contact_id))
        sent_status = send_sms(contact.mobile_no, message)

        admin_message = AdminMessage.objects.create(
            contact=contact,
            sender='admin',
            content=message,
            sent_status=sent_status
        )

        return JsonResponse({
            'success': sent_status,
            'message': 'Message sent to contact!' if sent_status else 'Failed to send message.',
            'message_id': admin_message.id,
            'sent_status': sent_status
        }, status=200 if sent_status else 500)

    year = filters.get('year')
    payment_mode = filters.get('payment_mode')
    paid = filters.get('paid')

    year_filter_int = int(dt.now().year)
    month_filter_int = int(dt.now().month)

    contacts_query = Business.objects.all()
    if paid == 'paid':
        contacts_query = [c for c in contacts_query if c.has_paid(year_filter_int, month_filter_int)]
    elif paid == 'unpaid':
        contacts_query = [c for c in contacts_query if not c.has_paid(year_filter_int, month_filter_int)]

    if year and year.isdigit():
        contacts_query = contacts_query.filter(
            id__in=BusinessYear.objects.filter(year=int(year)).values_list('business_id', flat=True)
        )

    if payment_mode:
        contacts_query = contacts_query.filter(payment_mode__id=payment_mode)

    failed_numbers = []
    for contact in contacts_query:
        sent_status = send_sms(contact.mobile_no, message)

        AdminMessage.objects.create(
            contact=contact,
            sender='admin',
            content=message,
            sent_status=sent_status
        )

        if not sent_status:
            failed_numbers.append(contact.mobile_no)

    if failed_numbers:
        return JsonResponse({
            'success': False,
            'message': f"Failed to send SMS to some numbers: {', '.join(failed_numbers)}",
            'failed_numbers': failed_numbers 
        }, status=500)

    return JsonResponse({'success': True, 'message': 'Message sent to all contacts!'})



