from django.contrib import admin
from .models import *

admin.site.register(User)

class PictureAdmin(admin.ModelAdmin):
	list_display = ('business_name','image_tag')
	list_filter = ('business_name',)
	search_fields = ('business_name',)
	
	def image_tag(self, obj):
		if obj.picture:
			return format_html('<img src="{}" style="width:auto; max-width:100px; height:auto"; />', obj.picture.url)
		return "No Image"
		
	image_tag.short_description = 'Image'

admin.site.register(Picture,PictureAdmin)