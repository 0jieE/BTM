from django.shortcuts import render

from rest_framework import viewsets

from .serializers import UserSerializer, BusinessSerializer, CollectionSerializer, PictureSerializer, BusinessYearSerializer
from home.models import Business, Collection, Picture, User, BusinessYear

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    def get_queryset(self):
        return self.queryset
    

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    def get_queryset(self):
        return self.queryset
    
class PictureViewSet(viewsets.ModelViewSet):
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

    def get_queryset(self):
        return self.queryset
    
class BusinessYearViewSet(viewsets.ModelViewSet):
    queryset = BusinessYear.objects.all()
    serializer_class = BusinessYearSerializer

    def get_queryset(self):
        return self.queryset