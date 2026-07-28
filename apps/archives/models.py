from django.db import models
from apps.notices.models import GlobalNotice

class ArchivedGlobalNotice(GlobalNotice):
    class Meta:
        proxy = True
        app_label = 'archives'
        verbose_name = "Archived Notice"
        verbose_name_plural = "Archived Notices"

from apps.mou.models import MOU

class ArchivedMOU(MOU):
    class Meta:
        proxy = True
        app_label = 'archives'
        verbose_name = "Archived MOU"
        verbose_name_plural = "Archived MOUs"

# Admissions
from apps.admission.models import AdmissionNotice, AdmissionCommitteeMinutes

class ArchivedAdmissionNotice(AdmissionNotice):
    class Meta:
        proxy = True
        app_label = 'archives'
        verbose_name = "Archived Admission Notice"
        verbose_name_plural = "Archived Admission Notices"

class ArchivedAdmissionCommitteeMinutes(AdmissionCommitteeMinutes):
    class Meta:
        proxy = True
        app_label = 'archives'
        verbose_name = "Archived Admission Committee Minutes"
        verbose_name_plural = "Archived Admission Committee Minutes"

# Authorities
from apps.authorities.models import (
    BoardOfManagementMinutes,
    AcademicCouncilMinutes,
    PlanningBoardMinutes,
    FinanceCommitteeMinutes,
)

class ArchivedBoardOfManagementMinutes(BoardOfManagementMinutes):
    class Meta:
        proxy = True
        app_label = 'archives'
        verbose_name = "Archived BoM Minutes"
        verbose_name_plural = "Archived BoM Minutes"

class ArchivedAcademicCouncilMinutes(AcademicCouncilMinutes):
    class Meta:
        proxy = True
        app_label = 'archives'
        verbose_name = "Archived Academic Council Minutes"
        verbose_name_plural = "Archived Academic Council Minutes"

class ArchivedPlanningBoardMinutes(PlanningBoardMinutes):
    class Meta:
        proxy = True
        app_label = 'archives'
        verbose_name = "Archived Planning Board Minutes"
        verbose_name_plural = "Archived Planning Board Minutes"

class ArchivedFinanceCommitteeMinutes(FinanceCommitteeMinutes):
    class Meta:
        proxy = True
        app_label = 'archives'
        verbose_name = "Archived Finance Committee Minutes"
        verbose_name_plural = "Archived Finance Committee Minutes"


