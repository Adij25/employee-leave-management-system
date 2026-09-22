from django.db import models
from django.conf import settings
from django.utils import timezone

class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    default_days = models.IntegerField(default=0)
    def __str__(self):
        return self.name

class EmployeeLeaveBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    casual = models.FloatField(default=0)
    sick = models.FloatField(default=0)
    other = models.FloatField(default=0)
    def __str__(self):
        return f"Balance for {self.user}"

class LeaveRequest(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.FloatField()
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', editable=False,
        help_text='Controlled by the admin approval workflow. Employees cannot change this field.'
    )
    applied_at = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.user} - {self.leave_type} ({self.start_date} to {self.end_date})"
