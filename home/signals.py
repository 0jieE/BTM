from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Business, Collection
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Business)
def link_collections_to_business(sender, instance, created, **kwargs):
    logger.debug(f"Received post_save signal for business {instance.business_no}")
    if created:
        logger.debug(f"Linking existing collections to new business: {instance.business_no} - {instance.business_name}")
        collections = Collection.objects.filter(business_no=instance.business_no, business_name=instance.business_name, linked_business__isnull=True)
        for collection in collections:
            collection.linked_business = instance
            collection.save()

@receiver(post_save, sender=Collection)
def link_collection_to_business(sender, instance, created, **kwargs):
    if created:
        try:
            business = Business.objects.get(business_no=instance.business_no, business_name=instance.business_name)
            instance.linked_business = business
            instance.save()
        except Business.DoesNotExist:
            logger.debug(f"Business with business_no {instance.business_no} and business_name {instance.business_name} does not exist.")