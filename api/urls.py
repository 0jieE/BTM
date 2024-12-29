from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import UserViewSet, BusinessViewSet, CollectionViewSet, PictureViewSet, BusinessYearViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('businesses', BusinessViewSet, basename='businesses')
router.register('collections', CollectionViewSet, basename='collections')
router.register('pictures', PictureViewSet, basename='pictures')
router.register('business-years', BusinessYearViewSet, basename="business_years")

urlpatterns = [
    path('', include(router.urls)),
]
