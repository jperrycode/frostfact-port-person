# apps.py
from django.apps import AppConfig

class FrostapiConfig(AppConfig):
    name = 'frostapi'

    def ready(self):
        import frostapi.signals
