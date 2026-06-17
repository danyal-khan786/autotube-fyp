from django.apps import AppConfig


class AuthappConfig(AppConfig):
    name = 'AuthApp'
    def ready(self):
        # Import the signals when the app starts
        import AuthApp.signals