from django.apps import AppConfig
from health_check.plugins import plugin_dir


class HealthConfig(AppConfig):
    name = "apps.health"

    def ready(self):
        from .health_checks import (  # OnderhuurHitkansServiceCheck,
            BAGServiceCheck,
            BRKServiceCheck,
            CeleryExecuteTask,
            CeleryStuckTasks
        )

        plugin_dir.register(BAGServiceCheck)
        plugin_dir.register(BRKServiceCheck)
        plugin_dir.register(CeleryExecuteTask)
        plugin_dir.register(CeleryStuckTasks)
        # Only uncomment below if endpoints for OnderhuurHitkans are available on production
        # plugin_dir.register(OnderhuurHitkansServiceCheck)
