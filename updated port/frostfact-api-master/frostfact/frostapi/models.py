from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
import uuid
from rest_framework.authtoken.models import Token
from datetime import datetime
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
import logging
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from datetime import timezone as dt_timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class CustomS3Boto3Storage(S3Boto3Storage):
    location = ''
    file_overwrite = False
    default_acl = 'public-read'


def resize_and_save_image(instance, image_field, desired_height, bucket_name=str(settings.AWS_STORAGE_BUCKET_NAME),
                          region_name='us-west-1'):
    try:
        if image_field:
            print(f"Starting image processing for file: '{image_field.name}' in instance '{instance}'")

            # Open the image using Pillow
            img = Image.open(image_field)
            print(f"Image opened: name='{image_field.name}', mode='{img.mode}', format='{img.format}', size={img.size}")

            # Calculate the corresponding width to maintain aspect ratio
            aspect_ratio = img.width / img.height
            new_width = int(desired_height * aspect_ratio)
            print(f"Calculated aspect ratio: {aspect_ratio:.2f}, resizing to: {new_width}x{desired_height}")

            # Resize the image
            img = img.resize((new_width, desired_height), Image.Resampling.LANCZOS)
            print(f"Image resized to: {new_width}x{desired_height}")

            # Save the image as WebP
            img_io = BytesIO()

            if img.mode != "RGBA" and img.mode != "RGB":
                img = img.convert("RGBA")
                print(f"Converted image to RGBA mode for WebP format")

            img.save(img_io, format='WEBP', optimize=True, quality=85)  # Optimize and reduce quality if needed
            print(f"Image saved to BytesIO as WebP with optimization")

            # Generate a safe filename using the instance's slug with .webp extension
            img_name = f"{slugify(instance.slug or 'image')}.webp"
            img_content = ContentFile(img_io.getvalue(), img_name)
            print(f"Generated image name for S3: '{img_name}'")

            # Upload to S3
            s3 = boto3.client('s3', region_name=region_name)
            key = f"{img_name}"
            print(f"Preparing to upload to S3 bucket '{bucket_name}' with key '{key}'")

            response = s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=img_content,
                ContentType='image/webp',  # WebP content type
                ACL='public-read'
            )
            print(f"S3 Response: {response}")

            print(f"Successfully uploaded image to S3: bucket='{bucket_name}', key='{key}', content_type='image/webp', ACL='public-read'")

            # Update the image field with the S3 key
            print(f"Image processing complete for file '{image_field.name}', S3 key: '{key}'")
            return key

    except Exception as e:
        logger.error(f"Error processing image '{image_field.name}' for instance '{instance}': {e}")
        print(f"Error processing image '{image_field.name}' for instance '{instance}': {e}")
        raise e



def default_time():
    return timezone.now().astimezone(dt_timezone.utc).time()


def default_date():
    return timezone.now().date()


def generate_unique_slug(model_class, field_value):
    """
    Generates a unique slug for a given model and field value.
    """
    base_slug = slugify(field_value)
    unique_slug = base_slug
    num = 1
    while model_class.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{base_slug}-{num}"
        num += 1
    return unique_slug


class HeroImage(models.Model):
    hero_image = models.ImageField(upload_to='', storage=CustomS3Boto3Storage(), blank=True,null=True, verbose_name="Hero Image")
    hero_image_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Hero Image Name')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", editable=False)
    hero_image_live = models.BooleanField(default=False, verbose_name='Image Live')
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Hero Slug", editable=False)

    class Meta:
        verbose_name = "Hero Image"
        verbose_name_plural = "Hero Images"

    def __str__(self):
        return self.hero_image_name or "Unnamed Image"

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.hero_image_name:
                self.slug = generate_unique_slug(HeroImage, self.hero_image_name)
            else:
                self.slug = generate_unique_slug(HeroImage, "hero-image")  # Fallback slug

        if self.hero_image:
            self.hero_image = resize_and_save_image(
                instance=self,
                image_field=self.hero_image,
                desired_height=1080,
                bucket_name=str(settings.AWS_STORAGE_BUCKET_NAME)
            )

        super(HeroImage, self).save(*args, **kwargs)


class ClientProfile(models.Model):
    client_first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Client's First Name")
    client_last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Client's Last Name")
    client_business = models.CharField(max_length=255, verbose_name="Client's Business")
    client_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Client's Phone")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Address")
    client_email = models.EmailField(unique=True, verbose_name="Client's Email")
    client_event_space = models.CharField(max_length=255, verbose_name="Client's Event Space")
    client_special_needs = models.TextField(blank=True, null=True, verbose_name="Client's Special Needs")
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Client Slug", editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(ClientProfile, f'{self.client_last_name}-{self.client_business}')
        super(ClientProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_first_name} {self.client_last_name} - {self.client_business}"


class ContactFormSubmission(models.Model):
    customer_email = models.EmailField(verbose_name="Customer's Email", default="Enter Email Address Here", blank=True)
    subject = models.CharField(max_length=255, blank=True, null=True, verbose_name="Subject")
    client_profile = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='contact_forms',
                                       verbose_name="Client Profile", null=True, blank=True)
    phone = models.CharField(max_length=12, blank=True, null=True, verbose_name="Phone Number")
    first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="First Name")
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Last Name")
    event_date_request = models.DateField(default=default_date, verbose_name="Event Date")
    message = models.TextField(verbose_name="Message", default='Tell us about your event')
    time_stamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp", blank=True, null=True,
                                      editable=False)
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Contact Slug", editable=False)
    message_read = models.BooleanField(default=False)
    csrf_token = models.CharField(max_length=100, null=True, blank=True, verbose_name="CSRF Token")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(ContactFormSubmission, f'{self.last_name}-{self.first_name}')


        is_new = self._state.adding
        super(ContactFormSubmission, self).save(*args, **kwargs)

        if is_new and not self.client_profile:
            self.run_after_save()




    def __str__(self):
        return f"Submission by {self.customer_email} on {self.time_stamp}"

    def run_after_save(self):
        if not self.client_profile:
            client_profile, created = ClientProfile.objects.get_or_create(
                client_email=self.customer_email,
                defaults={
                    'client_first_name': self.first_name,
                    'client_last_name': self.last_name,
                    'client_phone': self.phone
                }
            )
            if created:
                self.client_profile = client_profile
                # Save again if a new ClientProfile was created
                self.save()


@receiver(post_save, sender=ContactFormSubmission)
def execute_after_save(sender, instance, created, **kwargs):
    if created:
        instance.run_after_save()


class EventData(models.Model):
    class EventTypeChoices(models.TextChoices):
        MUSIC = 'Music', 'Music'
        THEATRE = 'Theatre', 'Theatre'
        WRESTLING = 'Wrestling', 'Wrestling'
        MARKET = 'Market', 'Market'
        PRIVATE_PARTY = 'Private Party', 'Private Party'

    MONTH_CHOICES = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]

    event_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Event Name")
    event_venue = models.CharField(max_length=30, blank=True, null=True, verbose_name="Event Venue")
    event_date = models.DateField(default=default_date, verbose_name="Event Date")
    event_month = models.CharField(max_length=15, choices=MONTH_CHOICES, null=True, blank=False,
                                   verbose_name='Event Month')
    event_type = models.CharField(max_length=20, choices=EventTypeChoices, blank=True, null=True,
                                  verbose_name="Event Type")
    event_genre = models.CharField(max_length=30, blank=True, null=True, verbose_name='Event Genre')
    event_time = models.TimeField(default=default_time, verbose_name="Event Time")
    recurring = models.BooleanField(default=False, verbose_name="Recurring Event?", null=True, blank=True)
    event_host = models.CharField(max_length=255, blank=True, null=True, verbose_name="Event Host")
    client_profile = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='events',
                                       verbose_name="Client Profile")
    event_image = models.ImageField(
        upload_to='',
        storage=CustomS3Boto3Storage(),
        blank=True,
        null=True,
        verbose_name='Image Upload'
    )
    event_description = models.TextField(blank=True, null=True, verbose_name="Event Description")
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Event Slug", editable=False)
    time_stamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp", blank=True, null=True,
                                      editable=False)
    artist_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Artist Name")
    artist_instagram = models.URLField(validators=[URLValidator()], blank=True, null=True, verbose_name='Instagram')
    artist_spotify = models.URLField(validators=[URLValidator()], blank=True, null=True, verbose_name='spotify')
    artist_youtube = models.URLField(validators=[URLValidator()], blank=True, null=True, verbose_name='youtube')
    artist_facebook = models.URLField(validators=[URLValidator()], blank=True, null=True, verbose_name='Facebook')

    def save(self, *args, **kwargs):
        # Generate slug if it doesn't exist
        if not self.slug:
            self.slug = generate_unique_slug(EventData, self.event_name)

        # Set event_month based on event_date
        if self.event_date:
            month_number = self.event_date.month
            self.event_month = dict(self.MONTH_CHOICES).get(month_number)

        if self.event_image:
            self.event_image = resize_and_save_image(
                instance=self,
                image_field=self.event_image,
                desired_height=500,
                bucket_name=str(settings.AWS_STORAGE_BUCKET_NAME)
            )

        # Save the instance
        super(EventData, self).save(*args, **kwargs)

    def __str__(self):
        return self.event_name

    class Meta:
        ordering = ['event_date']
        verbose_name_plural = 'Event Entry'
        verbose_name = 'Events Entry'


class FAQData(models.Model):
    faq_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='FAQ Title')
    faq_descrip = models.TextField(blank=True, null=True, verbose_name='FAQ Description')

    class Meta:
        verbose_name_plural = 'FAQ Entry'

    def __str__(self):
        return self.faq_title


class PolicyData(models.Model):
    policy_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='Policy Title')
    policy_descrip = models.TextField(blank=True, null=True, verbose_name='Policy Description')

    class Meta:
        verbose_name_plural = 'Policy Entry'

    def __str__(self):
        return self.policy_title


class GalleryData(models.Model):
    class MediaChoices(models.TextChoices):
        IMAGE = 'image', 'image'
        VIDEO = 'video', 'video'

    class EventChoices(models.TextChoices):
        SLIDER_TOP = 'slider top', 'slider top'
        SLIDER_BOTTOM = 'slider bottom', 'slider bottom'

    gallery_media_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='Image/Video Title')
    gallery_media_description = models.TextField(blank=True, null=True, verbose_name='Image/Video Description')
    gallery_media_image = models.ImageField(
        upload_to='',
        storage=CustomS3Boto3Storage(),
        blank=True,
        null=True,
        verbose_name='Image Upload'
    )
    gallery_media_video = models.URLField(validators=[URLValidator()], blank=True, null=True, verbose_name='Video Link')
    gallery_media_date = models.DateTimeField(auto_now=True, verbose_name="Image/Video Date")
    gallery_media_type = models.CharField(max_length=100, choices=MediaChoices, blank=True, null=True,
                                          verbose_name='Media Type')
    gallery_position = models.CharField(max_length=100, choices=EventChoices, blank=False, null=False,
                                          verbose_name='Gallery Position', default=EventChoices.SLIDER_TOP)
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="gallery Slug", editable=False)

    class Meta:
        verbose_name = 'Gallery image Entry'
        verbose_name_plural = 'Gallery images Entry'

    def __str__(self):
        return self.gallery_media_title

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = generate_unique_slug(GalleryData, self.gallery_media_title)

        if self.gallery_media_image:
            self.gallery_media_image = resize_and_save_image(
                instance=self,
                image_field=self.gallery_media_image,
                desired_height=500,
                bucket_name=str(settings.AWS_STORAGE_BUCKET_NAME)
            )

        super(GalleryData, self).save(*args, **kwargs)


class TextSliderTop(models.Model):
    top_slider_title = models.CharField(max_length=20, blank=True, null=True)
    top_slider_text = models.CharField(max_length=100, blank=True, null=True, verbose_name='Slider Top Text')
    active_text = models.BooleanField(default=False, null=True, verbose_name='Active Text')

    def __str__(self):
        return self.top_slider_title

    class Meta:
        verbose_name_plural = 'Text Slider Top'
        verbose_name = 'Text Slider Top'


class TextSliderBottom(models.Model):
    bottom_slider_title = models.CharField(max_length=20, blank=True, null=True)
    bottom_slider_text = models.CharField(max_length=100, blank=True, null=True, verbose_name='Slider Bottom Text')
    active_text = models.BooleanField(default=False, null=True, verbose_name='Active Text')

    def __str__(self):
        return self.bottom_slider_title

    class Meta:
        verbose_name_plural = 'Text Slider Bottom'
        verbose_name = 'Text Slider Bottom'
