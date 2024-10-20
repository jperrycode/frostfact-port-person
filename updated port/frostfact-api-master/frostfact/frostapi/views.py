from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from base64 import b64decode
from .serializers import *
from django.core.exceptions import SuspiciousOperation
import logging
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.exceptions import APIException
from django.middleware.csrf import get_token

# Set up logging
logger = logging.getLogger(__name__)

# Caching utility for signals
def get_cache_key(model_name):
    return f'{model_name}_queryset'


# CacheMixin for handling get/set cache logic
class CacheMixin:
    @staticmethod
    def get_or_set_cache(cache_key, queryset_func, timeout=60 * 60 * 24):
        logger.debug(f"Attempting to get cache for key: {cache_key}")
        try:
            queryset = cache.get(cache_key)
            if queryset is None:
                logger.info(f"Cache miss for key: {cache_key}")
                queryset = list(queryset_func())
                if not queryset:
                    logger.warning(f"No data found for {cache_key}.")
                    raise ValidationError(f"No data found for {cache_key}.")
                cache.set(cache_key, queryset, timeout=timeout)
                logger.info(f"Cache set for key: {cache_key} with timeout {timeout} seconds.")
            else:
                logger.info(f"Cache hit for key: {cache_key}")
            return queryset
        except ValidationError as e:
            error_message = ', '.join(e.detail) if isinstance(e.detail, list) else str(e.detail)
            logger.error(f"Validation error: {error_message}")
            raise SuspiciousOperation(error_message)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise SuspiciousOperation(f"An unexpected error occurred: {str(e)}")




# BaseAuthenticatedView with basic auth and caching

class BaseAuthenticatedView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_credentials(self, request):
        """Extract and decode credentials from the Authorization header."""
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Basic '):
                encoded_credentials = auth_header.split(' ')[1]
                decoded_credentials = b64decode(encoded_credentials).decode('utf-8')
                username, password = decoded_credentials.split(':')
                return username, password
            return None, None
        except (ValueError, IndexError, Exception) as e:
            logger.error(f"Error decoding credentials: {e}")
            raise AuthenticationFailed("Invalid or malformed credentials provided.")

    def authenticate(self, request):
        """Authenticate the user using basic auth credentials."""
        try:
            username, password = self.get_credentials(request)
            if not username or not password:
                raise AuthenticationFailed('Invalid credentials: Username and password required.')

            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise AuthenticationFailed('Invalid username or password.')
        except User.DoesNotExist:
            logger.warning(f"Authentication failed: User '{username}' does not exist.")
            raise AuthenticationFailed('Invalid username or password.')
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            raise APIException('An error occurred during authentication.')

    def get(self, request, slug=None, *args, **kwargs):
        """Handle GET requests with optional slug."""
        try:
            self.authenticate(request)
            if slug:
                instance = get_object_or_404(self.get_queryset(), slug=slug)
                serializer = self.get_serializer(instance)
            else:
                instances = self.get_queryset()
                serializer = self.get_serializer(instances, many=True)
            return Response(serializer.data)
        except AuthenticationFailed as af:
            logger.warning(f"Authentication failed in GET request: {af}")
            return Response({"success": False, "error": str(af)}, status=401)
        except Exception as e:
            logger.error(f"Error in GET request: {e}")
            raise APIException("An error occurred while processing the GET request.")

    def post(self, request, *args, **kwargs):
        """Handle POST requests with authentication."""
        try:
            # Authenticate the user
            self.authenticate(request)

            # Extract CSRF token from the request (if present)
            csrf_token = get_token(request)  # Alternatively, use get_token(request) if needed

            # Serialize and validate the incoming data
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                # Save the serializer and pass the CSRF token to be saved in the model
                serializer.save(csrf_token=csrf_token)

                # Perform any additional create logic
                self.perform_create(serializer)

                # Return success response with CSRF token included
                return Response({
                    "success": True,
                    "data": serializer.data,
                    "csrf_token": csrf_token  # Include the CSRF token in the response
                }, status=201)
            else:
                logger.warning(f"POST validation failed: {serializer.errors}")
                return Response({
                    "success": False,
                    "errors": serializer.errors
                }, status=400)
        except AuthenticationFailed as af:





            
            logger.warning(f"Authentication failed in POST request: {af}")
            return Response({
                "success": False,
                "error": str(af)
            }, status=401)
        except Exception as e:
            logger.error(f"Error in POST request: {e}")
            raise APIException("An error occurred while processing the POST request.")



# BaseCachedListView with caching support
class BaseCachedListView(CacheMixin, BaseAuthenticatedView, generics.ListCreateAPIView):
    cache_key_prefix = ""

    def get_cache_key(self):
        return f"{self.cache_key_prefix}_queryset"

    def get_queryset(self):
        cache_key = self.get_cache_key()
        return self.get_or_set_cache(cache_key, lambda: self.queryset.all())

# Define each view by extending BaseCachedListView and setting the appropriate serializer, queryset, and cache key prefix
def get_csrf_token(request):
    try:
        csrf_token = get_token(request)
        return JsonResponse({'success': True, 'csrfToken': csrf_token}, status=200)
    except SuspiciousOperation as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An unexpected error occurred: ' + str(e)}, status=500)
class ContactFormApiView(BaseCachedListView):
    serializer_class = ContactFormSerializer
    queryset = ContactFormSubmission.objects.all()
    cache_key_prefix = 'contact_form'

class HeroImageApiView(BaseCachedListView):
    serializer_class = HeroImageDataSerializer
    queryset = HeroImage.objects.filter(hero_image_live=True)
    cache_key_prefix = 'hero_image'


class EventApiView(BaseCachedListView):
    serializer_class = EventDataSerializer
    queryset = EventData.objects.all()
    cache_key_prefix = 'event_data'


class ClientApiView(BaseCachedListView):
    serializer_class = ClientProfileSerializer
    queryset = ClientProfile.objects.prefetch_related('contact_submissions', 'events')
    cache_key_prefix = 'client_data'

    def get_ordering(self):
        """Retrieve the ordering parameter with a fallback."""
        try:
            ordering = self.request.query_params.get('ordering', 'start_datetime')
            if not ordering:
                raise ValueError("Ordering parameter is missing.")
            return ordering
        except Exception as e:
            logger.error(f"Error fetching ordering parameter: {e}")
            raise APIException("Invalid ordering parameter.")  # Return a proper API error

    def get_cache_key(self):
        """Generate cache key based on the ordering."""
        try:
            ordering = self.get_ordering()
            return f"{self.cache_key_prefix}_queryset_{ordering}"
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            raise APIException("Failed to generate cache key.")  # Propagate as an API error

    def get_queryset(self):
        """Use cached queryset with ordering."""
        try:
            cache_key = self.get_cache_key()
            return self.get_or_set_cache(
                cache_key,
                lambda: self.queryset.order_by(self.get_ordering())
            )
        except FieldError as fe:
            logger.error(f"Invalid field used for ordering: {fe}")
            raise APIException("Invalid field specified for ordering.")
        except ImproperlyConfigured as ic:
            logger.error(f"Configuration error: {ic}")
            raise APIException("Server configuration error.")
        except Exception as e:
            logger.error(f"Error fetching queryset: {e}")
            raise APIException("An error occurred while retrieving data.")

class PolicyApiView(BaseCachedListView):
    serializer_class = PolicyDataSerializer
    queryset = PolicyData.objects.all()
    cache_key_prefix = 'policy_data'


class FaqApiView(BaseCachedListView):
    serializer_class = FaqDataSerializer
    queryset = FAQData.objects.all()
    cache_key_prefix = 'faq_data'


class GalleryApiView(BaseCachedListView):
    serializer_class = GalleryDataSerializer
    queryset = GalleryData.objects.all()
    cache_key_prefix = 'gallery_data'


class TextSliderTopApiView(BaseCachedListView):
    serializer_class = TextSliderTopSerializer
    queryset = TextSliderTop.objects.filter(active_text=True)
    cache_key_prefix = 'text_slider_top'


class TextSliderBottomApiView(BaseCachedListView):
    serializer_class = TextSliderBottomSerializer
    queryset = TextSliderBottom.objects.filter(active_text=True)
    cache_key_prefix = 'text_slider_bottom'
