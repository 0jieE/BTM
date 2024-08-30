from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),

    path('business/', views.business, name='business'),
    path('business/table', views.business_table, name='business-table'),
    path('collection/', views.collection, name='collection'),
    path('upload/business', views.UploadBusinessFileView, name='business-file'),
    path('upload/collection', views.UploadCollectionFileView, name='collection-file'),
    path('upload_pictures/', views.upload_pictures, name='upload-photos'),

    path('map/', views.map_view, name='map-view'),
    path('monthly-calculation/', views.monthly_calculation, name='monthly-calculation'),
    path('calculate/data', views.calculate_data, name='calculate_data'),
]
