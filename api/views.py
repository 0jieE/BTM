from django.shortcuts import render
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image
from PIL.ExifTags import TAGS

from rest_framework import viewsets

from .serializers import UserSerializer, BusinessSerializer, CollectionSerializer, PictureSerializer, BusinessYearSerializer
from home.models import Business, Collection, Picture, User, BusinessYear

def clean_image_metadata(image):
    try:
        img = Image.open(image)
        if hasattr(img, '_getexif'):
            exif_data = img._getexif()
            if exif_data:
                clean_exif = {}
                for tag, value in exif_data.items():
                    decoded = TAGS.get(tag, tag)
                    clean_exif[decoded] = value
                return clean_exif
    except Exception as e:
        print(f"Error processing EXIF data: {e}")
    return None

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
    parser_classes = [MultiPartParser, FormParser]
    

    def get_queryset(self):
        return self.queryset
    
    # def create(self, request, *args, **kwargs):
    #     image = request.FILES.get('picture')
    #     if image:
    #         exif_data = clean_image_metadata(image)
    #         print("EXIF Data:", exif_data)  # Debugging purpose
    #     return super().create(request, *args, **kwargs)
    
class BusinessYearViewSet(viewsets.ModelViewSet):
    queryset = BusinessYear.objects.all()
    serializer_class = BusinessYearSerializer

    def get_queryset(self):
        return self.queryset