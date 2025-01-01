from rest_framework import serializers

from home.models import User, Business, Collection, Picture, BusinessYear

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        # fields = '__all__'
        fields = ['id','business_no', 'business_name','last_name','first_name','middle_name',
                  'extension_name','gender','location','application_type','application_date',
                  'date_issued','capital_investment','gross_sales','payment_mode','business_type',
                  'business_nature','application_method','plate_no','mobile_no','latitude','longitude',
                ]


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id','business_no','business_name','payor','date_time','or_no','business_tax','permit','total']


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ['id','picture', 'picture_local', 'business_no', 'business', 'business_name']
        # fields = ['id','picture', 'picture_local', 'description', 'category', 'busineess_no','business','username']


class BusinessYearSerializer(serializers.ModelSerializer ):
    # business = BusinessSerializer()
    class Meta:
        model = BusinessYear
        fields = ['year', 'business']