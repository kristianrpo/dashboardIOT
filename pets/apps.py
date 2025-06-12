from django.apps import AppConfig
import os

class PetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pets'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        from .scheduler import start
        start()
