from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('staff/register/', views.staff_register, name='staff-register'),
    path('admin/register/', views.admin_register, name='admin-register'),

    path('business/', views.business, name='business'),
    path('edit/location/<int:pk>/', views.edit_location, name='edit-location'),
    path('location/<int:pk>/', views.location, name='location'),

    path('business/table', views.business_table, name='business-table'),
    path('collection/', views.collection, name='collection'),
    path('upload/business', views.UploadBusinessFileView, name='business-file'),
    path('upload/collection', views.UploadCollectionFileView, name='collection-file'),
    path('upload_pictures/', views.upload_pictures, name='upload-photos'),

    path('map/', views.map_view, name='map-view'),
    path('monthly-calculation/', views.monthly_calculation, name='monthly-calculation'),
    path('calculate/data', views.calculate_data, name='calculate_data'),

    path('user-logs/', views.user_logs_view, name='user_logs'),
    path('get-user-logs/<int:user_id>/', views.get_user_logs, name='get_user_logs'),
    path('user-logs/logs-pdf', views.logs_report_pdf, name='logs-pdf'),

    path('sms/', views.sms_view, name='sms'),
    path('api/get-contacts/', views.get_contacts, name='get_contacts'),
    path('api/get-messages/', views.get_messages, name='get_messages'),
    path('api/send-message/', views.send_message, name='send_message'),

]
