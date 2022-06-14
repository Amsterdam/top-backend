from django.apps import AppConfig
from health_check.plugins import plugin_dir


class HealthConfig(AppConfig):
    name = "apps.health"

    def ready(self):
        from .health_checks import (
            BAGServiceCheck,
            CeleryExecuteTask,
            OnderhuurHitkansServiceCheck,
            VakantieverhuurHitkansServiceCheck,
        )

        plugin_dir.register(BAGServiceCheck)
        plugin_dir.register(CeleryExecuteTask)
        plugin_dir.register(VakantieverhuurHitkansServiceCheck)
        # Only uncomment below if endpoints for OnderhuurHitkans are available on production
        # plugin_dir.register(OnderhuurHitkansServiceCheck)
