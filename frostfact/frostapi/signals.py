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

# ContactFormSubmission Cache Invalidation
@receiver(post_save, sender=ContactFormSubmission)
@receiver(post_delete, sender=ContactFormSubmission)
def invalidate_contact_form_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('contact_form_submission')
    cache.delete(cache_key)
    logger.info(f'Cache invalidated for {cache_key} (instance: {instance.pk})')

# EventData Cache Invalidation
@receiver(post_save, sender=EventData)
@receiver(post_delete, sender=EventData)
def invalidate_event_data_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('event_data')
    cache.delete(cache_key)
    logger.info(f'Cache invalidated for {cache_key} (instance: {instance.pk})')

# ClientProfile Cache Invalidation
@receiver(post_save, sender=ClientProfile)
@receiver(post_delete, sender=ClientProfile)
def invalidate_client_profile_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('client_profile')
    cache.delete(cache_key)
    logger.info(f'Cache invalidated for {cache_key} (instance: {instance.pk})')

# FAQData Cache Invalidation
@receiver(post_save, sender=FAQData)
@receiver(post_delete, sender=FAQData)
def invalidate_faq_data_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('faq_data')
    cache.delete(cache_key)
    logger.info(f'Cache invalidated for {cache_key} (instance: {instance.pk})')

# PolicyData Cache Invalidation
@receiver(post_save, sender=PolicyData)
@receiver(post_delete, sender=PolicyData)
def invalidate_policy_data_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('policy_data')
    cache.delete(cache_key)
    logger.info(f'Cache invalidated for {cache_key} (instance: {instance.pk})')

# TextSliderTop Cache Invalidation
@receiver(post_save, sender=TextSliderTop)
@receiver(post_delete, sender=TextSliderTop)
def invalidate_text_slider_top_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('text_slider_top')
    cache.delete(cache_key)
    logger.info(f'Cache invalidated for {cache_key} (instance: {instance.pk})')

# TextSliderBottom Cache Invalidation
@receiver(post_save, sender=TextSliderBottom)
@receiver(post_delete, sender=TextSliderBottom)
def invalidate_text_slider_bottom_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('text_slider_bottom')
    cache.delete(cache_key)
    logger.info(f'Cache invalidated for {cache_key} (instance: {instance.pk})')

# HeroImage Cache Invalidation
@receiver(post_save, sender=HeroImage)
@receiver(post_delete, sender=HeroImage)
def invalidate_hero_image_cache(sender, instance, **kwargs):
    cache_key = get_cache_key('hero_image')
    cache.delete(cache_key)
    logger.info(f'Cache invalidated for {cache_key} (instance: {instance.pk})')
