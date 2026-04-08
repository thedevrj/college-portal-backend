from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField

class School(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    image = models.ImageField(upload_to="schools/", blank=True, null=True)
    image_alt_text = models.CharField(max_length=255, blank=True, help_text="GIGW accessibility text for the image")
    dean = models.ForeignKey('faculty.Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='dean_of_schools')
    dean_message = RichTextField(blank=True)
    about_school = RichTextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.slug = self.slug[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Department(models.Model):
    school = models.ForeignKey(
        School,
        related_name="departments",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    hod = models.ForeignKey('faculty.Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='hod_of_departments')
    about = RichTextField(blank=True)
    thrust_areas = RichTextField(blank=True, help_text="Major research and academic focus areas of the department")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.slug = self.slug[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Program(models.Model):
    department = models.ForeignKey(Department, related_name="programs", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=50, choices=[('UG', 'Undergraduate'), ('PG', 'Postgraduate'), ('PHD', 'PhD'), ('Others', 'Others')])
    other_level = models.CharField(max_length=255, blank=True, null=True, help_text="Please specify the level if 'Others' is selected")
    duration = models.CharField(max_length=100,null=True, blank=True, help_text="e.g., 4 Years, 6 Semesters")
    intake = models.CharField(max_length=100,null=True, blank=True, help_text="Number of seats available")
    fees = models.CharField(max_length=255, blank=True, null=True, help_text="Fee structure details")
    eligibility = RichTextField(blank=True, null=True, help_text="Eligibility criteria for the program")
    admission_process = RichTextField(blank=True, null=True, help_text="Admission process for the program")
    syllabus = models.FileField(upload_to="programs/syllabus/", blank=True, null=True, help_text="Downloadable syllabus document")
    program_outcomes = RichTextField(blank=True, null=True, help_text="Detailed program outcomes/objectives")
    def clean(self):
        super().clean()
        if self.level == 'Others' and not self.other_level:
            raise ValidationError({'other_level': "This field is required when level is 'Others'."})

    def __str__(self):
        return f"{self.name} - {self.department.name}"

class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ('Core', 'Core'),
        ('Elective', 'Elective'),
        ('Compulsory Elective', 'Compulsory Elective'),
        ('Compulsory Foundation', 'Compulsory Foundation'),
        ('Practical', 'Practical'),
        ('Others', 'Others'),
    ]
    program = models.ForeignKey(Program, related_name="courses", on_delete=models.CASCADE)
    semester = models.PositiveIntegerField(help_text="e.g., 1, 2, 3...")
    course_code = models.CharField(max_length=50)
    course_title = models.CharField(max_length=255)
    credits = models.PositiveIntegerField()
    course_type = models.CharField(max_length=50, choices=COURSE_TYPE_CHOICES, default='Core')
    other_course_type = models.CharField(max_length=100, blank=True, null=True, help_text="Please specify if course type is 'Others'")

    class Meta:
        ordering = ['semester', 'course_code']

    def clean(self):
        super().clean()
        if self.course_type == 'Others' and not self.other_course_type:
            from django.core.exceptions import ValidationError
            raise ValidationError({'other_course_type': "This field is required when course type is 'Others'."})

    def __str__(self):
        return f"{self.course_code} - {self.course_title}"

class CBCSCourse(models.Model):
    department = models.ForeignKey(Department, related_name="cbcs_courses", on_delete=models.CASCADE, null=True, blank=True)
    semester = models.PositiveIntegerField(help_text="e.g., 1, 2, 3...")
    course_code = models.CharField(max_length=50)
    course_title = models.CharField(max_length=255)
    credits = models.PositiveIntegerField()

    class Meta:
        ordering = ['semester', 'course_code']

    def __str__(self):
        return f"CBCS: {self.course_code} - {self.course_title}"

def department_gallery_upload_path(instance, filename):
    # Creates a path like: departments/computer-science/gallery/image.png
    dept_slug = instance.department.slug if instance.department.slug else f"dept_{instance.department_id}"
    return f"departments/{dept_slug}/gallery/{filename}"

class DepartmentGallery(models.Model):
    department = models.ForeignKey(Department, related_name="gallery_images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=department_gallery_upload_path)
    caption = models.CharField(max_length=255, blank=True, null=True, help_text="Optional caption for the image")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Gallery image for {self.department.name}"

class Notice(models.Model):
    department = models.ForeignKey(Department, related_name="notices", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = RichTextField(blank=True)
    attachment = models.FileField(upload_to="notices/", blank=True, null=True)
    date_posted = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return self.title

class Committee(models.Model):
    department = models.ForeignKey(Department, related_name="committees", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = RichTextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

class CommitteeMember(models.Model):
    DESIGNATION_CHOICES = [
        ('Chairperson', 'Chairperson'),
        ('Member', 'Member'),
        ('Member & Convener', 'Member & Convener'),
        ('Others', 'Others'),
    ]
    committee = models.ForeignKey(Committee, related_name="members", on_delete=models.CASCADE)
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.CASCADE)
    designation_in_committee = models.CharField(max_length=100, choices=DESIGNATION_CHOICES)
    other_designation = models.CharField(max_length=100, blank=True, null=True, help_text="Please specify the designation if 'Others' is selected")

    def clean(self):
        super().clean()
        if self.designation_in_committee == 'Others' and not self.other_designation:
            raise ValidationError({'other_designation': "This field is required when designation is 'Others'."})

    def __str__(self):
        return f"{self.faculty.name} - {self.designation_in_committee}"

class ResearchProject(models.Model):
    department = models.ForeignKey(Department, related_name="research_projects", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    principal_investigator = models.ForeignKey('faculty.Faculty', related_name="pi_projects", on_delete=models.CASCADE)
    co_investigators = models.ManyToManyField('faculty.Faculty', related_name="co_pi_projects", blank=True)
    funding_agency = models.CharField(max_length=255)
    amount_sanctioned = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('Ongoing', 'Ongoing'), ('Completed', 'Completed')], default='Ongoing')

    def __str__(self):
        return self.title

class ResearchScholar(models.Model):
    department = models.ForeignKey(Department, related_name="scholars", on_delete=models.CASCADE)
    scholar_name = models.CharField(max_length=255)
    enrollment_no = models.CharField(max_length=50, unique=True)
    supervisor = models.ForeignKey('faculty.Faculty', related_name="supervised_scholars", on_delete=models.CASCADE)
    co_supervisor = models.ForeignKey('faculty.Faculty', related_name="co_supervised_scholars", on_delete=models.SET_NULL, null=True, blank=True)
    research_topic = models.CharField(max_length=500)
    registration_year = models.PositiveIntegerField()

    def __str__(self):
        return self.scholar_name

class Timetable(models.Model):
    department = models.ForeignKey(Department, related_name="timetables", on_delete=models.CASCADE)
    program = models.ForeignKey(Program, related_name="timetables", on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, help_text="e.g., B.Tech Sem 3 Timetable")
    attachment = models.FileField(upload_to="timetables/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class StudyMaterial(models.Model):
    department = models.ForeignKey(Department, related_name="study_materials", on_delete=models.CASCADE)
    program = models.ForeignKey(Program, related_name="study_materials", on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, help_text="e.g., Data Structures Lecture Notes")
    attachment = models.FileField(upload_to="study_materials/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title