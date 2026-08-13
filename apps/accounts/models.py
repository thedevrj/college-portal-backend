from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# --- Enums ---


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class PortalRole(models.TextChoices):
    DEAN = "DEAN", "Dean / Director"
    HOD = "HOD", "HOD / Coordinator"
    DEPT_STAFF = "DEPT_STAFF", "Department Staff"
    RD_ADMIN = "RD_ADMIN", "R&D Cell Admin"
    FACULTY = "FACULTY", "Faculty Member"
    COE = "COE", "Controller of Examinations"
    REGISTRAR = "REGISTRAR", "Registrar Office"
    FINANCE_SECTION = "FINANCE_SECTION", "Finance Section"
    ACADEMIC_SECTION = "ACADEMIC_SECTION", "Academic Section"


class EntityType(models.TextChoices):
    DEPARTMENT = "DEPARTMENT", "Department"
    SCHOOL = "SCHOOL", "School"
    CENTRE = "CENTRE", "Centre"


# --- Models ---


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="portal_profile"
    )
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        validators=[
            __import__(
                "django.core.validators", fromlist=["RegexValidator"]
            ).RegexValidator(
                regex=r"^\d{10}$",
                message="Phone number must be exactly 10 digits.",
            )
        ],
    )
    profile_photo = models.ImageField(
        upload_to="portal/profiles/", null=True, blank=True
    )
    is_portal_user = models.BooleanField(default=False)
    force_password_change = models.BooleanField(
        default=False,
        help_text="If True, the user will be forced to change their password on next login.",
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def is_rd_admin(self):
        return self.user.access_entries.filter(
            role=PortalRole.RD_ADMIN, is_active=True
        ).exists()

    def sync_permissions(self):
        from .services import PortalPermissionService

        PortalPermissionService.sync_user_permissions(self)

    def get_dashboard_stats(self):
        """Delegates calculation logic to the Stats Service."""
        from .services import PortalStatsService

        return PortalStatsService.get_user_stats(self)


class PortalAccess(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="access_entries"
    )
    role = models.CharField(max_length=50, choices=PortalRole.choices)
    entity_type = models.CharField(max_length=50, choices=EntityType.choices)

    # Made Nullable to prevent migration errors with existing data
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    entity = GenericForeignKey("content_type", "object_id")

    is_active = models.BooleanField(default=True)

    # Use 'created_at' to match your existing database name
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_accesses",
    )

    class Meta:
        verbose_name_plural = "Portal Access Entries"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} of {self.entity}"


class UserActivityLog(models.Model):
    class ActionType(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        LOGIN_FAILED = "LOGIN_FAILED", "Login Failed"

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=20, choices=ActionType.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "User Activity Logs"
        ordering = ["-timestamp"]

    def __str__(self):
        username = self.user.username if self.user else "Unknown User"
        return f"{username} - {self.get_action_display()} at {self.timestamp}"


# --- Signals ---


@receiver(post_save, sender=UserProfile)
def trigger_profile_sync(sender, instance, **kwargs):
    if instance.is_portal_user:
        instance.sync_permissions()


@receiver(post_save, sender=PortalAccess)
@receiver(models.signals.post_delete, sender=PortalAccess)
def trigger_access_sync(sender, instance, **kwargs):
    try:
        profile = getattr(instance.user, "portal_profile", None)
        if profile and profile.is_portal_user:
            profile.sync_permissions()
    except Exception:
        pass


# global trash bin


class GlobalTrashItem(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)

    item_name = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100)

    deleted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    deleted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Global Trash Item"
        verbose_name_plural = "(Recycle Bin)"
        ordering = ["-deleted_at"]

    def __str__(self):
        return f"{self.item_name}"
