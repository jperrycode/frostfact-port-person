# yourapp/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

# authentication.py (create this file in your app directory)
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from base64 import b64decode
from django.contrib.auth.models import User

class CustomHeaderAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        if not auth_header.startswith('Basic '):
            return None

        encoded_credentials = auth_header.split(' ')[1]
        decoded_credentials = b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':')

        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise AuthenticationFailed('Invalid username/password')
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid username/password')

        return (user, None)
