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
            "schoolboardcommitteemember",
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
            "invitedtalk",
            "coursedesign",
            "membership",
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
            "departmentgalleryevent",
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
            "cbcscourse",
            "committee",
            "researcharea",
            "committeemember",
            "minutesofthemeeting",
            "course",
            "departmentgallery",
            "departmentgalleryevent",
            "department",
            "faculty",
        ],
        PortalRole.RD_ADMIN: [
            "researchproject",
            "patent",
            "consultancy",
            "researcharea",
            "researchdevelopmentcellmember",
            "researchfacility",
            "faculty",
        ],
        PortalRole.COE: [
            "researchscholar",
            "coenotice",
            "phdvivavocedate",
            "mphilvivavocedate",
            "phdpresubmissionseminar",
            "rdcunotice",
            "faculty",
        ],
        PortalRole.REGISTRAR: [
            "boardofmanagementmember",
            "boardofmanagementminutes",
            "planningboardmember",
            "planningboardminutes",
            "academiccouncilmember",
            "academiccouncilminutes",
        ],
        PortalRole.FINANCE_SECTION: [
            "financecommitteemember",
            "financecommitteeminutes",
        ],
        PortalRole.VC_SECRETARIAT: [
            "boardofmanagementmember",
            "boardofmanagementminutes",
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

            active_access_list = user.access_entries.filter(is_active=True)
            if not active_access_list.exists():
                return

            models_to_grant = set()
            for access in active_access_list:
                role_models = PortalConfig.ROLE_MODELS.get(access.role, [])
                models_to_grant.update(role_models)

            if any(access.role == PortalRole.REGISTRAR for access in active_access_list):
                permissions = Permission.objects.filter(
                    content_type__model__in=list(models_to_grant)
                ).filter(
                    Q(codename__startswith="view_") | Q(codename__startswith="add_")| Q(codename__startswith="change_") | Q(codename__startswith="delete_")
                )
            elif any(access.role == PortalRole.RD_ADMIN for access in active_access_list):
                permissions = Permission.objects.filter(
                    content_type__model__in=list(models_to_grant)
                ).filter(
                    Q(codename__startswith="view_") | Q(codename__startswith="add_")
                )
            elif any(access.role == PortalRole.VC_SECRETARIAT for access in active_access_list):
                permissions = Permission.objects.filter(
                    content_type__model__in=list(models_to_grant)
                ).filter(
                    Q(codename__startswith="view_") | Q(codename__startswith="add_")| Q(codename__startswith="change_") | Q(codename__startswith="delete_")
                )

            elif any(access.role == PortalRole.ACADEMIC_SECTION for access in active_access_list):
                permissions = Permission.objects.filter(
                    content_type__model__in=list(models_to_grant)
                ).filter(
                    Q(codename__startswith="view_") | Q(codename__startswith="add_")| Q(codename__startswith="change_") | Q(codename__startswith="delete_")
                )

            elif any(access.role == PortalRole.FINANCE_SECTION for access in active_access_list):
                permissions = Permission.objects.filter(
                    content_type__model__in=list(models_to_grant)
                ).filter(
                    Q(codename__startswith="view_") | Q(codename__startswith="add_")| Q(codename__startswith="change_") | Q(codename__startswith="delete_")
                )
            else:
                permissions = Permission.objects.filter(
                    content_type__model__in=list(models_to_grant)
                ).filter(
                    Q(codename__startswith="view_")
                    | Q(codename__startswith="add_")
                    | Q(codename__startswith="change_")
                )
            permissions = permissions.exclude(codename="add_faculty")
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
        Return the stats of the projects, publications, scholars, etc.
        """
        user = user_profile.user
        active_access_list = user.access_entries.filter(is_active=True)
        if not active_access_list.exists():
            return {}

        try:
            Project = apps.get_model("research", "ResearchProject")
            Scholar = apps.get_model("research", "ResearchScholar")
            Pub = apps.get_model("research", "Publication")
            Faculty = apps.get_model("faculty", "Faculty")

            # Check if user has RD_ADMIN role -> global research stats
            if any(access.role == PortalRole.RD_ADMIN for access in active_access_list):
                projects_qs = Project.objects.filter(is_deleted=False)
                scholars_qs = Scholar.objects.filter(is_deleted=False)
                pubs_qs = Pub.objects.filter(is_deleted=False)
            else:
                projects_qs = Project.objects.none()
                scholars_qs = Scholar.objects.none()
                pubs_qs = Pub.objects.none()

                faculty_obj = Faculty.objects.filter(user=user).first()

                for access in active_access_list:
                    # 1. FACULTY Role
                    if access.role == PortalRole.FACULTY:
                        if faculty_obj:
                            scholars_qs |= Scholar.objects.filter(
                                Q(supervisor=faculty_obj) | Q(co_supervisor=faculty_obj)
                            )
                            pubs_qs |= Pub.objects.filter(internal_authors=faculty_obj)
                            projects_qs |= Project.objects.filter(
                                Q(principal_investigator=faculty_obj)
                                | Q(co_investigators=faculty_obj)
                            )

                    # 2. HOD or Department Role
                    elif (
                        access.role == PortalRole.HOD
                        or access.entity_type == EntityType.DEPARTMENT
                    ):
                        dept = access.entity
                        if dept:
                            scholars_qs |= Scholar.objects.filter(department=dept)
                            pubs_qs |= Pub.objects.filter(
                                internal_authors__department=dept
                            )
                            projects_qs |= Project.objects.filter(department=dept)

                    # 3. DEAN or School Role
                    elif (
                        access.role == PortalRole.DEAN
                        or access.entity_type == EntityType.SCHOOL
                    ):
                        school = access.entity
                        if school:
                            scholars_qs |= Scholar.objects.filter(
                                department__school=school
                            )
                            pubs_qs |= Pub.objects.filter(
                                internal_authors__department__school=school
                            )
                            projects_qs |= Project.objects.filter(
                                department__school=school
                            )

                projects_qs = projects_qs.filter(is_deleted=False).distinct()
                scholars_qs = scholars_qs.filter(is_deleted=False).distinct()
                pubs_qs = pubs_qs.filter(is_deleted=False).distinct()

            return {
                "projects": projects_qs.count(),
                "projects_ongoing": projects_qs.filter(
                    status__iexact="Ongoing"
                ).count(),
                "scholars": scholars_qs.count(),
                "scholars_active": scholars_qs.filter(
                    status__iexact="Pursuing"
                ).count(),
                "publications": pubs_qs.count(),
            }
        except Exception as e:
            logger.error(f"Fresh Stats Error: {e}")
            return {
                "projects": 0,
                "projects_ongoing": 0,
                "scholars": 0,
                "scholars_active": 0,
                "publications": 0,
            }

        return {}
