from django import forms
from django.utils import timezone
from .models import LeaveRequest

class LeaveApplyForm(forms.Form):
    leave_type = forms.ChoiceField(
        choices=[("casual", "Casual Leave"), ("sick", "Sick Leave"), ("other", "Other Leave")],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    reason = forms.CharField(required=False, max_length=500,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Add a short reason (optional)"}))

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        if start and start < timezone.localdate():
            self.add_error("start_date", "Leave cannot start in the past.")
        if start and end and end < start:
            self.add_error("end_date", "End date must be on or after the start date.")
        return cleaned
