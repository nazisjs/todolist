from django.apps import AppConfig


class TodoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "todo"

    def ready(self):
      from .views import start_scheduler
      start_scheduler()
