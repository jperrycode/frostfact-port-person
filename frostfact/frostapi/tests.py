from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from .models import ContactFormSubmission, HeroImage, EventData, ClientProfile, PolicyData, FAQData, GalleryData, TextSliderTop, TextSliderBottom

class APITestCase(TestCase):

    def setUp(self):
        # Set up the test environment and create test data
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create some test data for the various models
        self.contact_form = ContactFormSubmission.objects.create(
            customer_email="test@example.com",
            subject="Test Subject",
            message="Test Message"
        )
        self.hero_image = HeroImage.objects.create(hero_image_live=True)
        self.event_data = EventData.objects.create(event_name="Test Event")
        self.client_profile = ClientProfile.objects.create(business_name="Test Client")
        self.policy_data = PolicyData.objects.create(policy_name="Test Policy")
        self.faq_data = FAQData.objects.create(question="Test Question", answer="Test Answer")
        self.gallery_data = GalleryData.objects.create(title="Test Gallery")
        self.text_slider_top = TextSliderTop.objects.create(active_text=True)
        self.text_slider_bottom = TextSliderBottom.objects.create(active_text=True)

    def authenticate(self):
        # Helper function to authenticate the user
        credentials = b64encode(b'testuser:testpass').decode('utf-8')
        return {'HTTP_AUTHORIZATION': f'Basic {credentials}'}

    def test_get_csrf_token(self):
        response = self.client.get(reverse('csrf_token'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrfToken', response.json())

    def test_authentication_fail(self):
        response = self.client.get(reverse('client_api'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_success(self):
        response = self.client.get(reverse('client_api'), **self.authenticate())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contact_form_api_view(self):
        response = self.client.get(reverse('contact_form_api'), **self.authenticate())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Subject', str(response.content))

    def test_hero_image_api_view(self):
        response = self.client.get(reverse('hero_image_api'), **self.authenticate())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('true', str(response.content).lower())

    def test_event_api_view(self):
        response = self.client.get(reverse('event_api'), **self.authenticate())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Event', str(response.content))

    def test_client_api_view(self):
        response = self.client.get(reverse('client_api'), **self.authenticate())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Client', str(response.content))

    def test_policy_api_view(self):
        response = self.client.get(reverse('policy_api'), **self.authenticate())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Policy', str(response.content))

    def test_faq_api_view(self):
        response = self.client.get(reverse('faq_api'), **self.authenticate())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Question', str(response.content))

    def test_gallery_api_view(self):
        response = self.client.get(reverse('gallery_api'), **self.authenticate())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Gallery', str(response.content))

    def test_text_slider_top_api_view(self):
        response = self.client.get(reverse('text_slider_top_api'), **self.authenticate())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('true', str(response.content).lower())

    def test_text_slider_bottom_api_view(self):
        response = self.client.get(reverse('text_slider_bottom_api'), **self.authenticate())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('true', str(response.content).lower())
