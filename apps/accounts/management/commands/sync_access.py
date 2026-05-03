from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import PortalAccess, PortalRole, EntityType
from apps.academics.models import Department, School
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Bulk generate PortalAccess entries for all assigned HODs and Deans'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Syncing HOD and Dean access...")

        # 1. Sync HODs (Head of Departments)
        depts = Department.objects.filter(hod__isnull=False)
        hod_count = 0
        for dept in depts:
            user = dept.hod.user
            if user:
                # Ensure UserProfile exists and is marked as portal user
                profile = getattr(user, 'portal_profile', None)
                if profile:
                    profile.is_portal_user = True
                    profile.save()

                access, created = PortalAccess.objects.get_or_create(
                    user=user,
                    role=PortalRole.HOD,
                    entity_type=EntityType.DEPARTMENT,
                    object_id=dept.id,
                    content_type=ContentType.objects.get_for_model(Department)
                )
                if created:
                    hod_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✅ Created HOD access: {user.username} -> {dept.name}'))

        # 2. Sync Deans (Heads of Schools)
        schools = School.objects.filter(dean__isnull=False)
        dean_count = 0
        for school in schools:
            user = school.dean.user
            if user:
                # Ensure UserProfile exists and is marked as portal user
                profile = getattr(user, 'portal_profile', None)
                if profile:
                    profile.is_portal_user = True
                    profile.save()

                access, created = PortalAccess.objects.get_or_create(
                    user=user,
                    role=PortalRole.DEAN,
                    entity_type=EntityType.SCHOOL,
                    object_id=school.id,
                    content_type=ContentType.objects.get_for_model(School)
                )
                if created:
                    dean_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✅ Created DEAN access: {user.username} -> {school.name}'))

        self.stdout.write(self.style.SUCCESS(f'🎉 Sync complete! Added {hod_count} HODs and {dean_count} Deans.'))
