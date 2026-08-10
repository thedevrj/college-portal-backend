from django.db import models
from apps.notices.models import GlobalNotice


class ArchivedGlobalNotice(GlobalNotice):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived Notice"
        verbose_name_plural = "Archived Notices"


from apps.mou.models import MOU


class ArchivedMOU(MOU):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived MOU"
        verbose_name_plural = "Archived MOUs"


# Admissions
from apps.admission.models import AdmissionNotice, AdmissionCommitteeMinutes


class ArchivedAdmissionNotice(AdmissionNotice):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived Admission Notice"
        verbose_name_plural = "Archived Admission Notices"


class ArchivedAdmissionCommitteeMinutes(AdmissionCommitteeMinutes):
    class Meta:
        proxy = True
        app_label = "archives"
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
        app_label = "archives"
        verbose_name = "Archived BoM Minutes"
        verbose_name_plural = "Archived BoM Minutes"


class ArchivedAcademicCouncilMinutes(AcademicCouncilMinutes):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived Academic Council Minutes"
        verbose_name_plural = "Archived Academic Council Minutes"


class ArchivedPlanningBoardMinutes(PlanningBoardMinutes):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived Planning Board Minutes"
        verbose_name_plural = "Archived Planning Board Minutes"


class ArchivedFinanceCommitteeMinutes(FinanceCommitteeMinutes):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived Finance Committee Minutes"
        verbose_name_plural = "Archived Finance Committee Minutes"


from apps.proctor.models import ProctorialBoardNotice, ProctorialBoardMinutes


class ArchivedProctorialBoardNotice(ProctorialBoardNotice):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived Proctorial Board Notice"
        verbose_name_plural = "Archived Proctorial Board Notices"


class ArchivedProctorialBoardMinutes(ProctorialBoardMinutes):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived Proctorial Board Minutes"
        verbose_name_plural = "Archived Proctorial Board Minutes"


from apps.coe.models import (
    COENotice,
    PHDPreSubmissionSeminar,
    PHDVivaVoceDate,
    MPHILVivaVoceDate,
    RDCUNotice,
)


class ArchivedCOENotice(COENotice):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived COE Notice"
        verbose_name_plural = "Archived COE Notices"


class ArchivedPHDPreSubmissionSeminar(PHDPreSubmissionSeminar):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived PHD Pre Submission Seminar"
        verbose_name_plural = "Archived PHD Pre Submission Seminars"


class ArchivedPHDVivaVoceDate(PHDVivaVoceDate):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived PHD Viva Voce Date"
        verbose_name_plural = "Archived PHD Viva Voce Dates"


class ArchivedMPHILVivaVoceDate(MPHILVivaVoceDate):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived MPHIL Viva Voce Date"
        verbose_name_plural = "Archived MPHIL Viva Voce Dates"


class ArchivedRDCUNotice(RDCUNotice):
    class Meta:
        proxy = True
        app_label = "archives"
        verbose_name = "Archived RDCU Notice"
        verbose_name_plural = "Archived RDCU Notices"
