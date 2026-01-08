# cms/apps.py
from django.apps import AppConfig

class CmsConfig(AppConfig):
    name = 'cms'

    def ready(self):
        import cms.signals  # This "wakes up" the signals