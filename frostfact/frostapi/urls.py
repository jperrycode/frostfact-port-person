
from django.urls import path, include

from .views import *
from . import views


urlpatterns = [
    path('contact-fsf/', ContactFormApiView.as_view(), name='cont_form_list'),
    path('contact-fsf/<slug:slug>/', ContactFormApiView.as_view(), name='cont_form_data'),
    path('event-fst/<slug:slug>/', EventApiView.as_view(), name='event_data_detail'),
    path('event-fst/', EventApiView.as_view(), name='event_data_list'),
    path('client-data/', ClientApiView.as_view(), name='client_data_list'),
    path('client-data/<slug:slug>/', ClientApiView.as_view(), name='client_data_detail'),
    path('faq-data/', FaqApiView.as_view(), name='faq_list'),
    path('policy-data/', PolicyApiView.as_view(), name='policy_list'),
    path('gallery-data/', GalleryApiView.as_view(), name='gallery_data_list'),
    path('gallery-data/<slug:slug>/', GalleryApiView.as_view(), name='gallery_data_detail'),
    path('slider-top/', TextSliderTopApiView.as_view(), name='slider_top_list'),
    path('slider-bottom/', TextSliderBottomApiView.as_view(), name='slider_bottom_list'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('hero-image/', HeroImageApiView.as_view(), name='hero_image'),

]