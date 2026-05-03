import logging
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from django.apps import apps
from .models import PortalRole, EntityType

logger = logging.getLogger(__name__)


class PortalConfig:
    # Define which models each role is allowed to see and manage
    ROLE_MODELS = {
        PortalRole.DEAN: [
            "school",
            "schoolboardcommittee",
            "schoolboardmom",
            "department",
            "faculty",
        ],
        PortalRole.FACULTY: [
            "faculty",
            "researchproject",
            "researchscholar",
            "publication",
            "patent",
            "consultancy",
        ],
        PortalRole.HOD: [
            "researchproject",
            "researchscholar",
            "publication",
            "patent",
            "consultancy",
            "program",
            "notice",
            "timetable",
            "studymaterial",
            "faculty",
            "cbcscourse",
            "committee",
            "minutesofthemeeting",
            "researcharea",
            "committeemember",
            "course",
            "departmentgallery",
            "department",
        ],
        PortalRole.DEPT_STAFF: [
            "researchproject",
            "researchscholar",
            "publication",
            "patent",
            "consultancy",
            "program",
            "notice",
            "timetable",
            "studymaterial",
            "faculty",
            "cbcscourse",
            "committee",
            "researcharea",
            "committeemember",
            "minutesofthemeeting",
            "course",
            "departmentgallery",
            "department",
        ],
        PortalRole.RD_ADMIN: [
            "researchproject",
            "researchscholar",
            "publication",
            "patent",
            "consultancy",
            "researcharea",
            "faculty",
            "researchdevelopmentcellmember",
        ],
    }


class PortalPermissionService:
    @staticmethod
    def sync_user_permissions(user_profile):
        user = user_profile.user
        try:
            if user_profile.is_portal_user and not user.is_staff:
                user.is_staff = True
                user.save()

            active_access = user.access_entries.filter(is_active=True).first()
            if not active_access:
                return

            models_to_grant = PortalConfig.ROLE_MODELS.get(active_access.role, [])

            permissions = Permission.objects.filter(
                content_type__model__in=models_to_grant
            ).filter(
                Q(codename__startswith="view_")
                | Q(codename__startswith="add_")
                | Q(codename__startswith="change_")
            )

            group, _ = Group.objects.get_or_create(
                name=f"Portal_AutoGroup_{user.username}"
            )
            group.permissions.set(permissions)
            user.groups.add(group)
        except Exception as e:
            logger.error(f"Sync Error: {e}")


class PortalStatsService:
    @staticmethod
    def get_user_stats(user_profile):
        """
        FRESH START: Returning simplified stats to verify connection.
        """
        user = user_profile.user
        access = user.access_entries.filter(is_active=True).first()

        if not access:
            return {}

        try:
            # We use the internal app names verified by diagnostic
            Project = apps.get_model("research", "ResearchProject")
            Scholar = apps.get_model("research", "ResearchScholar")
            Pub = apps.get_model("research", "Publication")

            if access.entity_type == EntityType.DEPARTMENT:
                dept = access.entity
                return {
                    "projects": Project.objects.filter(department=dept).count(),
                    "projects_ongoing": Project.objects.filter(
                        department=dept, status="ONGOING"
                    ).count(),
                    "scholars": Scholar.objects.filter(department=dept).count(),
                    "scholars_active": Scholar.objects.filter(
                        department=dept, scholar_status="ACTIVE"
                    ).count(),
                    "publications": Pub.objects.filter(department=dept).count(),
                }
        except Exception as e:
            logger.error(f"Fresh Stats Error: {e}")
            # Fallback to zeros so the boxes at least show up
            return {
                "projects": 0,
                "projects_ongoing": 0,
                "scholars": 0,
                "scholars_active": 0,
                "publications": 0,
            }

        return {}
