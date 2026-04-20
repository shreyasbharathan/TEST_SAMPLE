from django.db import models
from django.conf import settings
# Create your models here.



from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings

class Lead(models.Model):
    # Choice Sets
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONTACTED', 'Contacted'),
        ('QUALIFIED', 'Qualified'),
        ('LOST', 'Lost'),
    ]

    
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    address = models.TextField(blank=True, null=True)
    
    occupation = models.CharField(max_length=150, blank=True, null=True)
    
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    email = models.EmailField(unique=True)
    
    product_type = models.CharField(max_length=100, blank=True, null=True)
    
    delivery_channel = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Lead Source"
    )
    
    # 10. PEP (Politically Exposed Person)
    is_pep = models.BooleanField(default=False, verbose_name="PEP Status")
    
    # 11. Responsible (The User/Agent assigned)
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leads"
    )
    
    # 12. Stage (UI Column: Stage)
    stage = models.CharField(
        max_length=100, 
        default='Assigned', 
        help_text="Current pipeline stage"
    )
    
    # 13. Creation Date
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")
    
    # 14. Modified
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modified")

    # --- Additional fields from your previous code kept for functionality ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    is_favorite = models.BooleanField(default=False)
    progress_score = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.id})"

class LeadActivity(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)

    activity_type = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    user_icon = models.URLField(blank=True, null=True)

from django.conf import settings

class Note(models.Model):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField()
    is_internal = models.BooleanField(default=False)
    mentions = models.JSONField(default=list, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)



from .models import Lead


class Task(models.Model):

    TASK_TYPE_CHOICES = [
        ("Call", "Call"),
        ("Meeting", "Meeting"),
        ("Email", "Email"),
        ("Follow Up", "Follow Up"),
    ]

    task_type = models.CharField(
        max_length=50,
        choices=TASK_TYPE_CHOICES
    )

    due_date = models.DateTimeField()

    description = models.TextField()

    # ✅ Lead ForeignKey (NEW)
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    # ✅ Assigned user
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_tasks"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task_type} - {self.assigned_to}"
    
class InsuranceInfo(models.Model):
    lead = models.OneToOneField(
        Lead,
        on_delete=models.CASCADE,
        related_name="insurance_info"
    )

    type_of_health_insurance = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    currently_insured = models.BooleanField(null=True, blank=True)
    salary_band = models.CharField(max_length=50, null=True, blank=True)
    emirates_id = models.CharField(max_length=50, null=True, blank=True)
    preferred_hospitals_clinics = models.TextField(null=True, blank=True)
    specific_benefits = models.TextField(null=True, blank=True)
    basic_plan_type = models.CharField(max_length=50, null=True, blank=True)
    co_payment = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Insurance Info for Lead {self.lead.id}"