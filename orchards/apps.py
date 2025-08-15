from django.apps import AppConfig


class OrchardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orchards'

    def ready(self):
        from .mqtt import start_mqtt
        start_mqtt()
