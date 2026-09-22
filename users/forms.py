from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()
phone_validator = RegexValidator(r"^\+?[0-9]{10,15}$", "Enter a valid phone number (10–15 digits).")
pin_validator = RegexValidator(r"^[0-9]{4}$", "PIN must contain exactly 4 digits.")


class LoginForm(forms.Form):
    phone = forms.CharField(max_length=15, validators=[phone_validator],
                            widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "10-digit phone number", "autocomplete": "username"}))
    pin = forms.CharField(max_length=4, validators=[pin_validator], widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "4-digit PIN", "inputmode": "numeric", "autocomplete": "current-password"}))


class RegistrationForm(forms.ModelForm):
    pin = forms.CharField(label="Create 4-digit PIN", min_length=4, max_length=4,
                          validators=[pin_validator],
                          widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "4-digit PIN", "inputmode": "numeric", "autocomplete": "new-password"}))
    confirm_pin = forms.CharField(label="Confirm PIN", min_length=4, max_length=4,
                                  validators=[pin_validator],
                                  widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Re-enter PIN", "inputmode": "numeric", "autocomplete": "new-password"}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "department"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "name@example.com"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "10-digit phone number", "inputmode": "tel"}),
            "department": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Engineering"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("An account with this phone number already exists.")
        return phone

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("pin") != cleaned.get("confirm_pin"):
            raise forms.ValidationError("PIN and confirmation PIN do not match.")
        return cleaned


class PinChangeForm(forms.Form):
    old_pin = forms.CharField(max_length=4, validators=[pin_validator], widget=forms.PasswordInput(attrs={"class": "form-control", "inputmode": "numeric"}))
    new_pin = forms.CharField(max_length=4, validators=[pin_validator], widget=forms.PasswordInput(attrs={"class": "form-control", "inputmode": "numeric"}))
    confirm_pin = forms.CharField(max_length=4, validators=[pin_validator], widget=forms.PasswordInput(attrs={"class": "form-control", "inputmode": "numeric"}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_pin") != cleaned.get("confirm_pin"):
            raise forms.ValidationError("New PIN and confirmation PIN do not match.")
        if cleaned.get("old_pin") == cleaned.get("new_pin"):
            raise forms.ValidationError("New PIN must be different from the current PIN.")
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "department"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "department": forms.TextInput(attrs={"class": "form-control"}),
        }
