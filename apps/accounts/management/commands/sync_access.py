from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import PortalAccess, PortalRole, EntityType, UserProfile
from apps.academics.models import Department, School
from apps.faculty.models import Faculty
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Bulk generate User accounts for all Faculty and sync roles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="Force reset all existing faculty passwords to the universal default",
        )

    def handle(self, *args, **options):
        # UNIVERSAL PASSWORD for all portal users
        UNIVERSAL_PASSWORD = "Bbau@123"
        reset_passwords = options.get("reset_passwords")

        self.stdout.write("🔍 Starting Faculty Login Sync...")
        if reset_passwords:
            self.stdout.write(
                self.style.WARNING(
                    f" Password reset is ENABLED. All accounts will be set to: {UNIVERSAL_PASSWORD}"
                )
            )

        # --- PRE-SYNC CLEANUP ---
        # Deactivate all existing HOD and DEAN roles to ensure only current ones are active
        PortalAccess.objects.filter(role__in=[PortalRole.HOD, PortalRole.DEAN]).update(
            is_active=False
        )

        # 1. Sync ALL Faculty
        all_faculty = Faculty.objects.filter(
            staff_no__isnull=False, is_active=True
        ).select_related("user")

        fac_count = 0
        reset_count = 0

        for faculty in all_faculty:
            # Respect the user's preferred username pattern: fac_staffno
            username = "fac_" + str(faculty.staff_no)
            user = faculty.user
            is_new_account = False

            if not user:
                # Check if user exists by username but not linked to this faculty record
                user = User.objects.filter(username=username).first()
                if user:
                    faculty.user = user
                    faculty.save()

            if not user:
                # Create new user
                user = User.objects.create_user(
                    username=username,
                    email=faculty.insti_email or faculty.other_email or "",
                    password=UNIVERSAL_PASSWORD,
                    is_staff=True,
                )
                faculty.user = user
                faculty.save()
                fac_count += 1
                is_new_account = True
                self.stdout.write(f"🆕 Created account for: {username}")

            # Sync Basic Info to User object
            user.email = faculty.insti_email or faculty.other_email or user.email
            # Split faculty name correctly to avoid duplication
            user.first_name = faculty.name.split(" ")[0][:150]
            user.last_name = " ".join(faculty.name.split(" ")[1:])[:150]

            if reset_passwords:
                user.set_password(UNIVERSAL_PASSWORD)
                user.is_staff = True

            user.save()

            # Ensure UserProfile exists and is active
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.is_portal_user = True

            # AUTO-FILL PROFILE DETAILS FROM FACULTY RECORD
            profile.employee_id = str(faculty.staff_no)
            profile.phone = faculty.phone1 or profile.phone
            if faculty.photo:
                profile.profile_photo = faculty.photo

            # Force password change for NEW accounts OR if we are doing a bulk reset
            if is_new_account or reset_passwords:
                profile.force_password_change = True

            profile.save()

            # Assign basic FACULTY role
            access, _ = PortalAccess.objects.get_or_create(
                user=user,
                role=PortalRole.FACULTY,
                entity_type=EntityType.DEPARTMENT,
                object_id=faculty.department_id,
                content_type=(
                    ContentType.objects.get_for_model(Department)
                    if faculty.department_id
                    else None
                ),
            )
            access.is_active = True
            access.save()

        # 2. Sync HODs
        depts = Department.objects.filter(hod__isnull=False).select_related(
            "hod", "hod__user"
        )
        for dept in depts:
            if dept.hod.user:
                access, _ = PortalAccess.objects.get_or_create(
                    user=dept.hod.user,
                    role=PortalRole.HOD,
                    entity_type=EntityType.DEPARTMENT,
                    object_id=dept.id,
                    content_type=ContentType.objects.get_for_model(Department),
                )
                access.is_active = True
                access.save()
                dept.hod.user.portal_profile.sync_permissions()

        # 3. Sync Deans
        schools = School.objects.filter(dean__isnull=False).select_related(
            "dean", "dean__user"
        )
        for school in schools:
            if school.dean.user:
                access, _ = PortalAccess.objects.get_or_create(
                    user=school.dean.user,
                    role=PortalRole.DEAN,
                    entity_type=EntityType.SCHOOL,
                    object_id=school.id,
                    content_type=ContentType.objects.get_for_model(School),
                )
                access.is_active = True
                access.save()
                school.dean.user.portal_profile.sync_permissions()

        # 4. Sync All Portal User Permissions
        self.stdout.write(" Re-syncing permissions for all portal users...")
        for profile in UserProfile.objects.filter(is_portal_user=True):
            profile.sync_permissions()

        self.stdout.write(
            self.style.SUCCESS(
                f" Sync Complete!\n"
                f"Created: {fac_count} new accounts. "
                f"Reset/Updated: {reset_count} existing passwords."
            )
        )
