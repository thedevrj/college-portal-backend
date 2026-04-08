from django.db import models
from ckeditor.fields import RichTextField

class GlobalNotice(models.Model):
    CATEGORY_CHOICES = [
        ('Announcement', 'Announcement'),
        ('Event', 'Event'),
        ('Appointment', 'Appointment'),
        ('Tenders', 'Tenders'),
    ]
    
    title = models.CharField(max_length=500)
    content = RichTextField(blank=True, null=True, help_text="Detailed content of the notice")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    link = models.URLField(blank=True, null=True, help_text="Optional external link or relative URL")
    attachment = models.FileField(upload_to="global_notices/", blank=True, null=True)
    
    show_in_marquee = models.BooleanField(default=False, help_text="Show this notice in the scrolling marquee at the top of the homepage")
    is_active = models.BooleanField(default=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_posted']
        
    def __str__(self):
        return f"[{self.category}] {self.title}"
