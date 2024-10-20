from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import *
from .forms import EventDataForm

class CustomMediaMixin:
    """Mixin to add custom CSS and JS to all admin models."""
    class Media:
        css = {
            'all': ('/static/css/admin_spinner.css',)  # Path to your custom CSS file
        }
        js = ('/static/js/admin_spinner.js',)  # Path to your custom JS file

class SingleActiveAdmin(CustomMediaMixin, admin.ModelAdmin):
    """Admin model ensuring only one active entry at a time."""

    def save_model(self, request, obj, form, change):
        try:
            if getattr(obj, self.active_field):
                obj.__class__.objects.exclude(pk=obj.pk).update(**{self.active_field: False})
            super().save_model(request, obj, form, change)
        except Exception as e:
            self.message_user(request, f"Error saving model: {str(e)}", level='error')
            raise ValidationError(f"Error saving model: {str(e)}")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields[self.active_field].widget = admin.widgets.AdminRadioSelect(
            choices=[(True, 'Active'), (False, 'Inactive')]
        )
        return form

@admin.register(HeroImage)
class HeroImageAdmin(SingleActiveAdmin):
    model = HeroImage
    list_display = ('hero_image_name', 'hero_image', 'hero_image_live',)
    list_editable = ('hero_image_live',)
    list_filter = ('hero_image_live', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('hero_image', 'hero_image_name', 'hero_image_live')
    active_field = 'hero_image_live'
    save_as_continue = False

class ContactFormSubmissionInline(admin.StackedInline):
    model = ContactFormSubmission
    extra = 0
    fields = ('customer_email', 'subject', 'message', 'time_stamp')
    readonly_fields = ('time_stamp',)

class EventDataInline(admin.StackedInline):
    model = EventData
    extra = 0
    fields = ('event_name', 'event_date', 'event_host', 'event_image')
    readonly_fields = ('event_date',)
    list_filter = ['client_profile']

@admin.register(ClientProfile)
class ClientProfileAdmin(CustomMediaMixin, admin.ModelAdmin):
    list_display = (
        'client_last_name', 'client_first_name', 'client_business', 'client_phone', 'client_email',
        'client_event_space', 'client_special_needs'
    )
    search_fields = ["client_first_name", "client_email"]
    readonly_fields = ('slug',)
    inlines = [ContactFormSubmissionInline, EventDataInline]

@admin.register(ContactFormSubmission)
class ContactFormSubmissionAdmin(CustomMediaMixin, admin.ModelAdmin):
    list_display = ('customer_email', 'subject', 'combined_name', 'time_stamp', 'client_profile')
    search_fields = ('customer_email', 'subject', 'phone', 'first_name', 'last_name')
    autocomplete_fields = ('client_profile',)
    readonly_fields = ('slug', 'time_stamp', 'csrf_token',)
    ordering = ('-time_stamp',)
    list_filter = ('client_profile',)
    fields = [
        'customer_email', 'subject', 'client_profile', 'phone', 'first_name', 'last_name',
        'event_date_request', 'message', 'time_stamp', 'slug', 'message_read', 'csrf_token'
    ]

    def combined_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

@admin.register(EventData)
class EventDataAdmin(CustomMediaMixin, admin.ModelAdmin):
    form = EventDataForm
    list_display = (
        'event_name', 'event_genre', 'event_date', 'event_type', 'event_host', 'event_image', 'client_profile',
        'recurring', 'artist_name', 'artist_instagram', 'artist_spotify', 'artist_youtube', 'artist_facebook'
    )
    search_fields = ['event_name', 'client_profile__client_business', 'event_month', 'event_host', 'event_genre',
                     'recurring']
    readonly_fields = ('slug', 'event_month')
    fields = (
        'event_name', 'event_date', 'event_time', 'event_type', 'event_genre', 'event_host', 'recurring',
        'event_image', 'artist_name', 'artist_instagram', 'artist_spotify', 'artist_youtube', 'artist_facebook',
        'client_profile',
    )

    def save_model(self, request, obj, form, change):
        try:
            if not obj.event_month:
                obj.event_month = obj.event_date.strftime('%B')
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

@admin.register(FAQData)
class FAQDataAdmin(CustomMediaMixin, admin.ModelAdmin):
    list_display = ('faq_title', 'faq_descrip')
    search_fields = ('faq_title', 'faq_descrip')

@admin.register(PolicyData)
class PolicyDataAdmin(CustomMediaMixin, admin.ModelAdmin):
    list_display = ('policy_title', 'policy_descrip')
    search_fields = ('policy_title', 'policy_descrip')

@admin.register(GalleryData)
class GalleryDataAdmin(CustomMediaMixin, admin.ModelAdmin):
    list_display = ('gallery_media_title', 'gallery_media_description', 'gallery_media_image', 'gallery_media_date',
                    'gallery_media_type', 'gallery_position')
    search_fields = ('gallery_media_title', 'gallery_media_description', 'gallery_position')
    fields = (
        'gallery_media_title', 'gallery_media_description', 'gallery_media_image', 'gallery_media_video',
        'gallery_media_type', 'gallery_position',
    )

@admin.register(TextSliderTop)
class SliderTopAdmin(SingleActiveAdmin):
    list_display = ('top_slider_title', 'top_slider_text', 'active_text')
    active_field = 'active_text'

@admin.register(TextSliderBottom)
class SliderBottomAdmin(SingleActiveAdmin):
    list_display = ('bottom_slider_title', 'bottom_slider_text', 'active_text')
    active_field = 'active_text'
