from django.apps import AppConfig


class FarmConfig(AppConfig):
    name = 'farm'

    def ready(self):
        import farm.signals
