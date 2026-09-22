from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserCreationForm(forms.ModelForm):
    pin = forms.CharField(
        label="4-digit PIN",
        min_length=4,
        max_length=4,
        widget=forms.PasswordInput(attrs={"inputmode": "numeric"}),
    )

    class Meta:
        model = CustomUser
        fields = ("phone", "first_name", "last_name", "email", "employee_id", "department", "role")

    def clean_pin(self):
        pin = self.cleaned_data["pin"]
        if not pin.isdigit():
            raise forms.ValidationError("PIN must contain exactly 4 digits.")
        return pin

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["pin"])
        user.pin = ""
        if commit:
            user.save()
        return user


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    ordering = ("phone",)
    list_display = ("phone", "get_name", "employee_id", "department", "role", "is_active", "is_staff")
    list_filter = ("role", "department", "is_active", "is_staff")
    search_fields = ("phone", "first_name", "last_name", "email", "employee_id")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Employee details", {"fields": ("first_name", "last_name", "email", "employee_id", "department", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": (
            "phone", "first_name", "last_name", "email", "employee_id",
            "department", "role", "pin", "is_staff", "is_active"
        )}),
    )
    readonly_fields = ("date_joined", "last_login")

    def get_name(self, obj):
        return obj.get_full_name() or "—"
    get_name.short_description = "Name"
