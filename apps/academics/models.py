from django.db import models
from django.utils.text import slugify

class School(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    image = models.ImageField(upload_to="schools/", blank=True, null=True)
    image_alt_text = models.CharField(max_length=255, blank=True, help_text="GIGW accessibility text for the image")
    dean = models.ForeignKey('faculty.Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='dean_of_schools')
    about_school = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    mission = models.TextField(blank=True)
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
    about = models.TextField(blank=True)
    thrust_areas = models.TextField(blank=True, help_text="Major research and academic focus areas of the department")
    vision = models.TextField(blank=True)
    mission = models.TextField(blank=True)
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
    level = models.CharField(max_length=50, choices=[('UG', 'Undergraduate'), ('PG', 'Postgraduate'), ('PHD', 'PhD')])
    duration_years = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.department.name}"

class Notice(models.Model):
    department = models.ForeignKey(Department, related_name="notices", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
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
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

class CommitteeMember(models.Model):
    committee = models.ForeignKey(Committee, related_name="members", on_delete=models.CASCADE)
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.CASCADE)
    designation_in_committee = models.CharField(max_length=100) # e.g., Chairman, Convener, Member

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