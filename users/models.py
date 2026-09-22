from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, pin, first_name="", last_name="", email="", role="employee", **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")
        if not pin:
            raise ValueError("PIN is required")
        user = self.model(
            phone=phone.strip(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email.strip().lower(),
            role=role,
            **extra_fields,
        )
        user.set_password(pin)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, pin, **extra_fields):
        user = self.create_user(phone=phone, pin=pin, role="admin", **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (("admin", "Admin"), ("employee", "Employee"))

    phone = models.CharField(max_length=15, unique=True)
    # Kept only for backwards-compatible database migrations. Authentication uses
    # Django's hashed password field; this field is never used for authentication.
    pin = models.CharField(max_length=128, blank=True, editable=False)
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["pin"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name() or self.phone} ({self.phone})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
