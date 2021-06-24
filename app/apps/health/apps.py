from django.apps import AppConfig
from health_check.plugins import plugin_dir


class HealthConfig(AppConfig):
    name = "apps.health"

    def ready(self):
        from .health_checks import (
            BAGServiceCheck,
            BWVDatabaseCheck,
            CeleryExecuteTask,
            DecosJoinCheck,
            OnderhuurHitkansServiceCheck,
            VakantieverhuurHitkansServiceCheck,
        )

        plugin_dir.register(BAGServiceCheck)
        # plugin_dir.register(BWVDatabaseCheck)
        plugin_dir.register(CeleryExecuteTask)
        plugin_dir.register(DecosJoinCheck)
        plugin_dir.register(VakantieverhuurHitkansServiceCheck)
        plugin_dir.register(OnderhuurHitkansServiceCheck)
