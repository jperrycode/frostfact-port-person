from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
import logging
from .models import *

# Create a logger
logger = logging.getLogger(__name__)

def get_cache_key(model_name):
    """Generates a cache key for each model."""
    return f'{model_name}_queryset'

def get_instance_cache_key(instance):
    """Generates a cache key for a specific instance."""
    return f'{instance.__class__.__name__.lower()}_{instance.pk}_data'

def log_cache_status(action, model_name, cache_key, instance):
    """Log cache status with detailed information."""
    logger.info(f'{action} - Model: {model_name}, Cache Key: {cache_key}, Instance: {instance.pk}')
    if cache.get(cache_key) is not None:
        logger.info(f'Cache content: {cache.get(cache_key)}')
    else:
        logger.info('Cache is empty')

# Error handling wrapper for cache invalidation
def safe_invalidate_cache(cache_key, instance, model_name):
    try:
        cache.delete(cache_key)
        log_cache_status('Cache deleted', model_name, cache_key, instance)
    except Exception as e:
        logger.error(f"Error invalidating cache for {model_name}, Instance: {instance.pk}. Error: {str(e)}")


# ContactFormSubmission Cache Invalidation
@receiver(post_save, sender=ContactFormSubmission)
@receiver(post_delete, sender=ContactFormSubmission)
def invalidate_contact_form_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('contact_form_submission')
    safe_invalidate_cache(cache_key, instance, 'ContactFormSubmission')


# EventData Cache Invalidation
@receiver(post_save, sender=EventData)
@receiver(post_delete, sender=EventData)
def invalidate_event_data_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('event_data')
    safe_invalidate_cache(cache_key, instance, 'EventData')


# ClientProfile Cache Invalidation
@receiver(post_save, sender=ClientProfile)
@receiver(post_delete, sender=ClientProfile)
def invalidate_client_profile_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('client_profile')
    safe_invalidate_cache(cache_key, instance, 'ClientProfile')


# FAQData Cache Invalidation
@receiver(post_save, sender=FAQData)
@receiver(post_delete, sender=FAQData)
def invalidate_faq_data_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('faq_data')
    safe_invalidate_cache(cache_key, instance, 'FAQData')


# PolicyData Cache Invalidation
@receiver(post_save, sender=PolicyData)
@receiver(post_delete, sender=PolicyData)
def invalidate_policy_data_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('policy_data')
    safe_invalidate_cache(cache_key, instance, 'PolicyData')


# TextSliderTop Cache Invalidation
@receiver(post_save, sender=TextSliderTop)
@receiver(post_delete, sender=TextSliderTop)
def invalidate_text_slider_top_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('text_slider_top')
    safe_invalidate_cache(cache_key, instance, 'TextSliderTop')


# TextSliderBottom Cache Invalidation
@receiver(post_save, sender=TextSliderBottom)
@receiver(post_delete, sender=TextSliderBottom)
def invalidate_text_slider_bottom_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('text_slider_bottom')
    safe_invalidate_cache(cache_key, instance, 'TextSliderBottom')


# HeroImage Cache Invalidation
@receiver(post_save, sender=HeroImage)
@receiver(post_delete, sender=HeroImage)
def invalidate_hero_image_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('hero_image')
    safe_invalidate_cache(cache_key, instance, 'HeroImage')


# GalleryData Cache Invalidation
@receiver(post_save, sender=GalleryData)
@receiver(post_delete, sender=GalleryData)
def invalidate_gallery_data_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('gallery_data')
    safe_invalidate_cache(cache_key, instance, 'GalleryData')
