from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords
from apps.accounts.models import SoftDeleteModel


class School(SoftDeleteModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    image = models.ImageField(upload_to="schools/", blank=True, null=True)
    image_alt_text = models.CharField(
        max_length=255, blank=True, help_text="GIGW accessibility text for the image"
    )

    LEADERSHIP_TITLE_CHOICES = [
        ("Dean", "Dean"),
        ("Director", "Director"),
    ]
    leadership_title = models.CharField(
        max_length=50,
        choices=LEADERSHIP_TITLE_CHOICES,
        default="Dean",
    )
    dean = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dean_of_schools",
        verbose_name="Leadership",
    )
    dean_message = RichTextField(blank=True, null=True)
    about_school = RichTextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=10, blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["name"]

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        from django.core.validators import validate_email
        import re

        if self.contact_phone:
            val = str(self.contact_phone).strip()
            if not re.match(r"^\d{10}$", val):
                raise ValidationError(
                    {"contact_phone": "Phone number must be exactly 10 digits."}
                )
            self.contact_phone = val

        if self.contact_email:
            val = str(self.contact_email).strip().lower()
            try:
                validate_email(val)
            except ValidationError:
                raise ValidationError(
                    {"contact_email": "Please enter a valid email address."}
                )
            self.contact_email = val

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.slug = self.slug[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SchoolBoardCommittee(SoftDeleteModel):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="school_board_committee",
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    description = RichTextField(max_length=255, blank=True, null=True)
    notification_or_document = models.FileField(
        upload_to="schools/board-committee-documents/", null=True, blank=True
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "School Board Committee"

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class SchoolBoardCommitteeMember(SoftDeleteModel):
    DESIGNATION_CHOICES = [
        ("Chairperson", "Chairperson"),
        ("Member", "Member"),
        ("Member & Convener", "Member & Convener"),
        ("Others", "Others"),
    ]
    committee = models.ForeignKey(
        SchoolBoardCommittee,
        on_delete=models.CASCADE,
        related_name="members",
        null=True,
        blank=True,
    )
    members = models.CharField(max_length=255)
    designation = models.CharField(
        max_length=255,
        choices=DESIGNATION_CHOICES,
    )
    other_designation = models.CharField(max_length=255, blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "School Board Committee Members"

    def __str__(self):
        committee_name = (
            self.committee.school.name
            if self.committee and self.committee.school
            else "Unknown School"
        )
        return f"{self.members} - {self.designation} ({committee_name})"

    def clean(self):
        super().clean()
        if self.designation == "Others" and not self.other_designation:
            raise ValidationError(
                {
                    "other_designation": "This field is required when designation is 'Others'."
                }
            )


class SchoolBoardMOM(SoftDeleteModel):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="school_board_mom",
    )
    meeting_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of the Meeting",
    )
    date_of_meeting = models.DateField(
        help_text="Date of the Meeting in yyyy-mm-dd format"
    )
    minutes = models.FileField(
        upload_to="schools/school-board-mom/",
        help_text="Upload Minutes of the Meeting",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date_of_meeting"]
        verbose_name_plural = "School Board Minutes"

    def __str__(self):
        return f"School Board MOM - {self.school.name}"


class Department(SoftDeleteModel):
    CAMPUS_CHOICES = [
        ("BBAU", "BBAU"),
        ("Satellite Campus Amethi", "Satellite Campus Amethi"),
    ]

    school = models.ForeignKey(
        School,
        related_name="departments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)

    LEADERSHIP_TITLE_CHOICES = [
        ("HOD", "HOD"),
        ("Coordinator", "Coordinator"),
    ]
    leadership_title = models.CharField(
        max_length=50,
        choices=LEADERSHIP_TITLE_CHOICES,
        default="HOD",
    )
    hod = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hod_of_departments",
        verbose_name="Leadership",
    )
    history = HistoricalRecords()

    about = RichTextField(blank=True, null=True)
    thrust_areas = RichTextField(
        blank=True,
        null=True,
        help_text="Major research and academic focus areas of the department",
    )
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=10, blank=True, null=True)
    campus = models.CharField(max_length=50, choices=CAMPUS_CHOICES, default="BBAU")

    class Meta:
        ordering = ["name"]

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        from django.core.validators import validate_email
        import re

        if self.contact_phone:
            val = str(self.contact_phone).strip()
            if not re.match(r"^\d{10}$", val):
                raise ValidationError(
                    {"contact_phone": "Phone number must be exactly 10 digits."}
                )
            self.contact_phone = val

        if self.contact_email:
            val = str(self.contact_email).strip().lower()
            try:
                validate_email(val)
            except ValidationError:
                raise ValidationError(
                    {"contact_email": "Please enter a valid email address."}
                )
            self.contact_email = val

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Add campus suffix for satellite campuses to ensure slug uniqueness
            if self.campus != "BBAU":
                self.slug = f"{self.slug}-amethi"
        self.slug = self.slug[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        if self.campus != "BBAU":
            return f"{self.name} (Amethi)"
        return self.name


class Program(SoftDeleteModel):
    department = models.ForeignKey(
        Department,
        related_name="programs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    centre = models.ForeignKey(
        "centres.Centre",
        related_name="programs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255, verbose_name="Name of Program")
    level = models.CharField(
        max_length=50,
        choices=[
            ("UG", "Undergraduate"),
            ("PG", "Postgraduate"),
            ("Integrated", "Integrated"),
            ("PHD", "PhD"),
            ("Others", "Others"),
        ],
    )
    other_level = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Please specify the level if 'Others' is selected",
    )
    duration = models.CharField(
        max_length=100, null=True, blank=True, help_text="e.g., 4 Years, 6 Semesters"
    )
    intake = models.CharField(
        max_length=100, null=True, blank=True, help_text="Number of seats available"
    )
    fees = RichTextField(blank=True, null=True, help_text="Fee structure details")
    eligibility = RichTextField(
        blank=True, null=True, help_text="Eligibility criteria for the program"
    )
    admission_process = RichTextField(
        blank=True, null=True, help_text="Admission process for the program"
    )
    notification_or_document_file = models.FileField(
        upload_to="programs/documents/",
        blank=True,
        null=True,
        help_text="Downloadable document related to the program",
    )
    syllabus = models.FileField(
        upload_to="programs/syllabus/",
        blank=True,
        null=True,
        help_text="Downloadable syllabus document",
    )
    program_outcomes = RichTextField(
        blank=True, null=True, help_text="Detailed program outcomes/objectives"
    )
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if self.level == "Others" and not self.other_level:
            raise ValidationError(
                {"other_level": "This field is required when level is 'Others'."}
            )
        if not self.department and not self.centre:
            raise ValidationError(
                "A program must be associated with either a Department or a Centre."
            )
        if self.department and self.centre:
            raise ValidationError(
                "A program cannot be associated with both a Department and a Centre."
            )

    def __str__(self):
        owner = (
            self.department.name
            if self.department
            else self.centre.name if self.centre else "Unknown"
        )
        return f"{self.name} - {owner}"


class Course(SoftDeleteModel):
    COURSE_TYPE_CHOICES = [
        ("Core", "Core"),
        ("Elective", "Elective"),
        ("Compulsory Elective", "Compulsory Elective"),
        ("Compulsory Foundation", "Compulsory Foundation"),
        ("Practical", "Practical"),
        ("Others", "Others"),
    ]
    program = models.ForeignKey(
        Program, related_name="courses", on_delete=models.CASCADE, null=True, blank=True
    )
    semester = models.PositiveIntegerField(
        help_text="e.g., 1, 2, 3...", null=True, blank=True
    )
    course_code = models.CharField(max_length=100, verbose_name="Course/ Paper Code")
    course_title = models.CharField(max_length=255)
    credits = models.PositiveIntegerField()
    course_type = models.CharField(
        max_length=50, choices=COURSE_TYPE_CHOICES, null=True, blank=True
    )
    other_course_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Please specify if course type is 'Others'",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ["semester", "course_code"]
        verbose_name_plural = "Course structure"

    def clean(self):
        super().clean()
        if self.course_type == "Others" and not self.other_course_type:
            raise ValidationError(
                {
                    "other_course_type": "This field is required when course type is 'Others'."
                }
            )

    def __str__(self):
        return f"{self.course_code} - {self.course_title}"


class CBCSCourse(SoftDeleteModel):
    department = models.ForeignKey(
        Department,
        related_name="cbcs_courses",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    centre = models.ForeignKey(
        "centres.Centre",
        related_name="cbcs_courses",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    program = models.ForeignKey(
        Program,
        related_name="cbcs_courses",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    semester = models.PositiveIntegerField(help_text="e.g., 1, 2, 3...")
    course_code = models.CharField(max_length=50)
    course_title = models.CharField(max_length=255)
    credits = models.PositiveIntegerField()
    syllabus = models.FileField(
        upload_to="cbcs_courses/syllabus/",
        blank=True,
        null=True,
        help_text="Downloadable syllabus document",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ["semester", "course_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["department", "course_code"],
                condition=models.Q(is_deleted=False, department__isnull=False),
                name="unique_cbcscourse_dept_code",
            ),
            models.UniqueConstraint(
                fields=["centre", "course_code"],
                condition=models.Q(is_deleted=False, centre__isnull=False),
                name="unique_cbcscourse_centre_code",
            ),
        ]

    def clean(self):
        super().clean()
        if not self.department and not self.centre:
            raise ValidationError(
                "A CBCS Course must be associated with either a Department or a Centre."
            )
        if self.department and self.centre:
            raise ValidationError(
                "A CBCS Course cannot be associated with both a Department and a Centre."
            )
        # Duplicate course_code check within the same department or centre
        qs = CBCSCourse.objects.filter(
            course_code__iexact=self.course_code,
            is_deleted=False,
        )
        if self.department:
            qs = qs.filter(department=self.department)
        elif self.centre:
            qs = qs.filter(centre=self.centre)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                {
                    "course_code": f"A course with code '{self.course_code}' already exists in this department/centre."
                }
            )

    def __str__(self):
        return f"CBCS: {self.course_code} - {self.course_title}"


def department_gallery_upload_path(instance, filename):
    # Creates a path like: departments/computer-science/gallery/image.png
    # department is always set (NOT NULL) so no null-guard needed.
    dept_slug = instance.department.slug or f"dept_{instance.department_id}"
    if getattr(instance, "event", None):
        event_slug = slugify(instance.event.title)
        return f"departments/{dept_slug}/gallery/events/{event_slug}/{filename}"
    return f"departments/{dept_slug}/gallery/{filename}"


class DepartmentGalleryEvent(SoftDeleteModel):
    department = models.ForeignKey(
        Department, related_name="gallery_events", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    date_of_event = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date_of_event", "-created_at"]
        verbose_name_plural = "Department Event Gallery"

    def __str__(self):
        return f"{self.title} ({self.department.name})"


class DepartmentGallery(SoftDeleteModel):
    department = models.ForeignKey(
        Department, related_name="gallery_images", on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        DepartmentGalleryEvent,
        related_name="images",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to=department_gallery_upload_path)
    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional caption for the image",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def clean(self):
        super().clean()
        if self.event_id:
            self.department = self.event.department

    def __str__(self):
        if self.event:
            return f"Gallery image for event: {self.event.title}"
        return f"Gallery image for {self.department.name}"


class Notice(SoftDeleteModel):
    NOTICE_CATEGORY_CHOICES = [
        ("General", "General"),
        ("Academic", "Academic"),
        ("Examination", "Examination"),
        ("Admission", "Admission"),
        ("Scholarship", "Scholarship"),
        ("Others", "Others"),
    ]
    department = models.ForeignKey(
        Department,
        related_name="notices",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    centre = models.ForeignKey(
        "centres.Centre",
        related_name="notices",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=NOTICE_CATEGORY_CHOICES)
    other_category = models.CharField(
        max_length=100, blank=True, null=True, help_text="Specify if 'Others' selected"
    )
    content = RichTextField(blank=True, null=True)
    attachment = models.FileField(upload_to="notices/", blank=True, null=True)
    date_posted = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date_posted"]

    def clean(self):
        super().clean()
        if self.category == "Others" and not self.other_category:
            raise ValidationError(
                {"other_category": "This field is required when category is 'Others'."}
            )
        if not self.department and not self.centre:
            raise ValidationError(
                "A Notice must be associated with either a Department or a Centre."
            )
        if self.department and self.centre:
            raise ValidationError(
                "A Notice cannot be associated with both a Department and a Centre."
            )

    def __str__(self):
        return f"[{self.category}] {self.title}"


class Committee(SoftDeleteModel):
    COMMITTEE_CHOICES = [
        ("DRC", "Departmental Research Committee (DRC)"),
        ("BPGS", "Board of Post Graduate Studies (BPGS)"),
        ("BUGS", "Board of Under Graduate Studies (BUGS)"),
        ("DPC", "Departmental Purchase Committee (DPC)"),
        ("Others", "Others"),
    ]
    department = models.ForeignKey(
        Department,
        related_name="committees",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    centre = models.ForeignKey(
        "centres.Centre",
        related_name="committees",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=255, choices=COMMITTEE_CHOICES, verbose_name="Name of Committee"
    )
    other_name = models.CharField(
        max_length=255, blank=True, null=True, help_text="Specify if 'Others' selected"
    )
    notification_document = models.FileField(
        upload_to="committees/notification/",
        blank=True,
        null=True,
        help_text="Notification or document related to the committee",
    )
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if self.name == "Others" and not self.other_name:
            raise ValidationError(
                {"other_name": "This field is required when name is 'Others'."}
            )
        if not self.department and not self.centre:
            raise ValidationError(
                "A Committee must be associated with either a Department or a Centre."
            )
        if self.department and self.centre:
            raise ValidationError(
                "A Committee cannot be associated with both a Department and a Centre."
            )

    def __str__(self):
        display_name = (
            self.other_name
            if self.name == "Others" and self.other_name
            else self.get_name_display()
        )
        owner = (
            self.department.name
            if self.department
            else self.centre.name if self.centre else "Unknown"
        )
        return f"{display_name} ({owner})"

    class Meta:
        verbose_name_plural = "Departmental Committees"


class CommitteeMember(SoftDeleteModel):
    DESIGNATION_CHOICES = [
        ("Chairperson", "Chairperson"),
        ("Member", "Member"),
        ("Member & Convener", "Member & Convener"),
        ("Others", "Others"),
    ]
    committee = models.ForeignKey(
        Committee,
        related_name="members",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name_of_member = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Name of Committee Member"
    )
    designation_in_committee = models.CharField(
        max_length=100, choices=DESIGNATION_CHOICES
    )
    other_designation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Please specify the designation if 'Others' is selected",
    )
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if self.designation_in_committee == "Others" and not self.other_designation:
            raise ValidationError(
                {
                    "other_designation": "This field is required when designation is 'Others'."
                }
            )

    def __str__(self):
        return f"{self.name_of_member} - {self.designation_in_committee}"

    class Meta:
        verbose_name_plural = "Departmental Committee Members"


class MinutesOfTheMeeting(SoftDeleteModel):
    committee = models.ForeignKey(
        Committee,
        related_name="minutes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    meeting_number = models.IntegerField(
        verbose_name="Meeting Number",
        null=True,
        blank=True,
        help_text="Enter the meeting number. Eg: 1st, 2nd, 3rd, etc.",
    )
    meeting_title = models.CharField(
        max_length=155, null=True, blank=True, help_text="Title of the meeting"
    )
    date_of_meeting = models.DateField(
        help_text="Enter date of meeting in YYYY-MM-DD format"
    )
    minutes_of_meeting = models.FileField(
        upload_to="committees/minutes/",
        help_text="Upload Minutes of the meeting",
    )
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if not self.committee:
            raise ValidationError(
                {"committee": "Minutes of Meeting must be associated with a committee."}
            )

    def __str__(self):
        committee_name = self.committee.name if self.committee else "Unknown Committee"
        return f"Minutes of {committee_name} - {self.date_of_meeting}"

    class Meta:
        ordering = ["-date_of_meeting"]
        verbose_name_plural = "Departmental Minutes "


class Timetable(SoftDeleteModel):
    department = models.ForeignKey(
        Department,
        related_name="timetables",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    centre = models.ForeignKey(
        "centres.Centre",
        related_name="timetables",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    program = models.ForeignKey(
        Program,
        related_name="timetables",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255, help_text="e.g., B.Tech Sem 3 Timetable")
    attachment = models.FileField(upload_to="timetables/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if not self.department and not self.centre:
            raise ValidationError(
                "Timetable must be associated with either a Department or a Centre."
            )
        if self.department and self.centre:
            raise ValidationError(
                "Timetable cannot be associated with both a Department and a Centre."
            )

    def __str__(self):
        return self.title


class StudyMaterial(SoftDeleteModel):
    department = models.ForeignKey(
        Department,
        related_name="study_materials",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    centre = models.ForeignKey(
        "centres.Centre",
        related_name="study_materials",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    program = models.ForeignKey(
        Program,
        related_name="study_materials",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    title = models.CharField(
        max_length=255, help_text="e.g., Data Structures Lecture Notes"
    )
    attachment = models.FileField(upload_to="study_materials/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if not self.department and not self.centre:
            raise ValidationError(
                "Study Material must be associated with either a Department or a Centre."
            )
        if self.department and self.centre:
            raise ValidationError(
                "Study Material cannot be associated with both a Department and a Centre."
            )

    def __str__(self):
        return self.title
