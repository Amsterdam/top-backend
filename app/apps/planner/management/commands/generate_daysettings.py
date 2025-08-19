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

        if options.get("cleanup"):
            DaySettings.objects.filter(team_settings__in=teams).delete()

        created, updated, skipped = 0, 0, 0

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
                    "week_day": idx,
                    "week_days": [idx],
                    "reasons": reasons_ids,
                    "state_types": state_types_ids,
                    "day_segments": day_segments_ids,
                    "week_segments": week_segments_ids,
                    "priorities": priorities_ids,
                }

                if options.get("dry_run"):
                    exists = DaySettings.objects.filter(
                        team_settings=team,
                        week_day=idx,
                    ).exists()
                    if exists:
                        skipped += 1
                    else:
                        created += 1
                    continue

                obj, was_created = DaySettings.objects.get_or_create(
                    team_settings=team,
                    week_day=idx,
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    changed = False
                    if obj.name != day_name:
                        obj.name = day_name
                        changed = True
                    if obj.week_days != [idx]:
                        obj.week_days = [idx]
                        changed = True
                    update_fields = ["name", "week_days"]
                    # Synchronize selectable arrays
                    if obj.reasons != reasons_ids:
                        obj.reasons = reasons_ids
                        changed = True
                        update_fields.append("reasons")
                    if obj.state_types != state_types_ids:
                        obj.state_types = state_types_ids
                        changed = True
                        update_fields.append("state_types")
                    if obj.day_segments != day_segments_ids:
                        obj.day_segments = day_segments_ids
                        changed = True
                        update_fields.append("day_segments")
                    if obj.week_segments != week_segments_ids:
                        obj.week_segments = week_segments_ids
                        changed = True
                        update_fields.append("week_segments")
                    if obj.priorities != priorities_ids:
                        obj.priorities = priorities_ids
                        changed = True
                        update_fields.append("priorities")
                    if changed:
                        obj.save(update_fields=update_fields)
                        updated += 1
                    else:
                        skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"DaySettings created={created}, updated={updated}, skipped={skipped}"
            )
        )
