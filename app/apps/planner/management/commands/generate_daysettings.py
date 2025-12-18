from apps.planner.models import DaySettings, TeamSettings
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from settings.const import WEEK_DAYS


class Command(BaseCommand):
    help = "Generate one DaySettings per weekday for each TeamSettings (7 per team)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show actions without writing",
        )
        parser.add_argument(
            "--exclude-disabled",
            action="store_true",
            help="Process only enabled teams",
        )
        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="Delete existing DaySettings for selected teams before creating",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        teams = TeamSettings.objects.all()
        if options.get("exclude-disabled"):
            teams = teams.filter(enabled=True)

        if options.get("cleanup") and not options.get("dry_run"):
            DaySettings.objects.filter(team_settings__in=teams).delete()

        created, skipped = 0, 0

        for team in teams:
            # Fetch selectable values once per team
            try:
                schedules = team.fetch_team_schedules()
            except Exception:
                schedules = {}
            try:
                reasons = team.fetch_team_reasons()
            except Exception:
                reasons = []

            day_segments_ids = [
                item.get("id") for item in schedules.get("day_segments", [])
            ]
            week_segments_ids = [
                item.get("id") for item in schedules.get("week_segments", [])
            ]
            priorities_ids = [
                item.get("id") for item in schedules.get("priorities", [])
            ]
            reasons_ids = [item.get("id") for item in reasons]
            state_types_ids = [
                item.get("id") for item in getattr(settings, "AZA_CASE_STATE_TYPES", [])
            ]

            for idx, day_name in enumerate(WEEK_DAYS):
                defaults = {
                    "name": "Standaard",
                    "week_days": [idx],
                    "reasons": reasons_ids,
                    "state_types": state_types_ids,
                    "day_segments": day_segments_ids,
                    "week_segments": week_segments_ids,
                    "priorities": priorities_ids,
                }

                exists = DaySettings.objects.filter(
                    team_settings=team,
                    week_days__contains=[idx],
                ).exists()

                if exists:
                    skipped += 1
                else:
                    created += 1

                if not exists and not options.get("dry_run"):
                    DaySettings.objects.create(
                        team_settings=team,
                        **defaults,
                    )

        self.stdout.write(
            self.style.SUCCESS(f"DaySettings created: {created}, skipped: {skipped}")
        )
