from django.core.management.base import BaseCommand
from apps.faculty.models import Faculty
from apps.faculty.orcid_sync import sync_faculty_orcid

class Command(BaseCommand):
    help = "Synchronizes faculty profile details, publications, and patents with their ORCID records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Synchronize all faculty members who have an ORCID ID set.",
        )
        parser.add_argument(
            "--staff-no",
            type=int,
            help="Synchronize a specific faculty member by their staff number.",
        )

    def handle(self, *args, **options):
        sync_all = options["all"]
        staff_no = options["staff_no"]

        if not sync_all and not staff_no:
            self.stdout.write(
                self.style.ERROR(
                    "You must specify either --all or --staff-no <number>. Run with -h for help."
                )
            )
            return

        if staff_no:
            queryset = Faculty.objects.filter(staff_no=staff_no)
            if not queryset.exists():
                self.stdout.write(
                    self.style.ERROR(f"No faculty member found with staff number: {staff_no}")
                )
                return
        else:
            queryset = Faculty.objects.filter(orcid_id__isnull=False).exclude(orcid_id="")

        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No faculty records found to synchronize."))
            return

        self.stdout.write(self.style.SUCCESS(f"Starting ORCID synchronization for {total} faculty profile(s)..."))

        success_count = 0
        fail_count = 0

        for faculty in queryset:
            if not faculty.orcid_id:
                self.stdout.write(
                    self.style.WARNING(f"Skipping {faculty.name} (Staff No: {faculty.staff_no}) — no ORCID ID set.")
                )
                continue

            self.stdout.write(f"Syncing {faculty.name} (ORCID: {faculty.orcid_id})...")
            result = sync_faculty_orcid(faculty)

            if result["success"]:
                self.stdout.write(self.style.SUCCESS(f"  -> {result['message']}"))
                success_count += 1
            else:
                self.stdout.write(self.style.ERROR(f"  -> Failed to sync {faculty.name}: {result['message']}"))
                fail_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nORCID synchronization completed. Successfully synced: {success_count}. Failed: {fail_count}."
            )
        )
