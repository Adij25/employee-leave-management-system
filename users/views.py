from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from leaves.models import EmployeeLeaveBalance
from .forms import LoginForm, PinChangeForm, ProfileForm, RegistrationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("leaves:dashboard")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(request, username=form.cleaned_data["phone"], password=form.cleaned_data["pin"])
        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or 'there'}!")
            return redirect("leaves:admin_dashboard" if user.role == "admin" else "leaves:dashboard")
        messages.error(request, "Invalid phone number or PIN.")
    return render(request, "users/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("leaves:dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        pin = form.cleaned_data["pin"]
        user.role = "employee"
        user.set_password(pin)
        user.pin = ""  # never store the PIN in plaintext
        user.save()
        user.employee_id = f"EMP-{user.pk:05d}"
        user.save(update_fields=["employee_id"])
        EmployeeLeaveBalance.objects.create(user=user, casual=12, sick=10, other=5)
        messages.success(request, "Account created successfully. You can now sign in.")
        return redirect("accounts:login")
    return render(request, "users/register.html", {"form": form})


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required
def profile(request):
    return render(request, "users/profile.html")


@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("accounts:profile")
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_pin(request):
    form = PinChangeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not request.user.check_password(form.cleaned_data["old_pin"]):
            form.add_error("old_pin", "Current PIN is incorrect.")
        else:
            request.user.set_password(form.cleaned_data["new_pin"])
            request.user.pin = ""
            request.user.save()
            messages.success(request, "PIN changed successfully. Please sign in again.")
            logout(request)
            return redirect("accounts:login")
    return render(request, "users/change_pin.html", {"form": form})
