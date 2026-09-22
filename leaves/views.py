from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import LeaveApplyForm
from .models import EmployeeLeaveBalance, LeaveRequest


@login_required
def dashboard(request):
    balance, _ = EmployeeLeaveBalance.objects.get_or_create(
        user=request.user, defaults={"casual": 12, "sick": 10, "other": 5}
    )
    requests = LeaveRequest.objects.filter(user=request.user).order_by("-applied_at")[:6]
    stats = {
        "total": LeaveRequest.objects.filter(user=request.user).count(),
        "pending": LeaveRequest.objects.filter(user=request.user, status="pending").count(),
        "approved": LeaveRequest.objects.filter(user=request.user, status="approved").count(),
    }
    return render(request, "leaves/dashboard.html", {"balance": balance, "requests": requests, "stats": stats})


@login_required
def apply_leave(request):
    form = LeaveApplyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        leave_type = form.cleaned_data["leave_type"]
        start, end = form.cleaned_data["start_date"], form.cleaned_data["end_date"]
        days = (end - start).days + 1
        balance, _ = EmployeeLeaveBalance.objects.get_or_create(
            user=request.user, defaults={"casual": 12, "sick": 10, "other": 5}
        )
        available = getattr(balance, leave_type, 0)
        overlap = LeaveRequest.objects.filter(
            user=request.user,
            status__in=["pending", "approved"],
            start_date__lte=end,
            end_date__gte=start,
        ).exists()
        if overlap:
            form.add_error(None, "You already have a pending or approved leave overlapping these dates.")
        elif days > available:
            form.add_error(None, f"Insufficient {leave_type} balance. Available: {available:g} day(s).")
        else:
            LeaveRequest.objects.create(
                user=request.user, leave_type=leave_type, start_date=start, end_date=end,
                days=days, reason=form.cleaned_data["reason"],
            )
            messages.success(request, "Leave request submitted for approval.")
            return redirect("leaves:leave_history")
    return render(request, "leaves/apply_leave.html", {"form": form})


@login_required
def leave_history(request):
    # Employees can only view their requests here. Approval status is
    # intentionally read-only and can only be changed by an admin through
    # the review_leave workflow below.
    requests = LeaveRequest.objects.filter(user=request.user).select_related("reviewed_by").order_by("-applied_at")
    return render(request, "leaves/leave_history.html", {"requests": requests})


def is_admin(user):
    return user.is_authenticated and (user.role == "admin" or user.is_superuser)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    pending = LeaveRequest.objects.filter(status="pending").select_related("user").order_by("applied_at")
    recent = LeaveRequest.objects.exclude(status="pending").select_related("user").order_by("-reviewed_at")[:10]
    stats = {
        "employees": request.user.__class__.objects.filter(role="employee").count(),
        "pending": LeaveRequest.objects.filter(status="pending").count(),
        "approved": LeaveRequest.objects.filter(status="approved").count(),
        "rejected": LeaveRequest.objects.filter(status="rejected").count(),
    }
    return render(request, "leaves/admin_dashboard.html", {"pending": pending, "recent": recent, "stats": stats})


@login_required
@user_passes_test(is_admin)
@transaction.atomic
def review_leave(request, pk, action):
    if request.method != "POST" or action not in {"approve", "reject"}:
        return redirect("leaves:admin_dashboard")
    lr = get_object_or_404(LeaveRequest.objects.select_for_update(), pk=pk)
    if lr.status != "pending":
        messages.warning(request, "This leave request has already been reviewed.")
        return redirect("leaves:admin_dashboard")
    lr.reviewed_by = request.user
    lr.reviewed_at = timezone.now()
    if action == "approve":
        balance, _ = EmployeeLeaveBalance.objects.select_for_update().get_or_create(
            user=lr.user, defaults={"casual": 12, "sick": 10, "other": 5}
        )
        available = getattr(balance, lr.leave_type, 0)
        if lr.days > available:
            messages.error(request, "Leave cannot be approved because the employee's current balance is insufficient.")
            return redirect("leaves:admin_dashboard")
        setattr(balance, lr.leave_type, available - lr.days)
        balance.save()
        lr.status = "approved"
        messages.success(request, "Leave request approved.")
    else:
        lr.status = "rejected"
        messages.success(request, "Leave request rejected.")
    lr.save()
    return redirect("leaves:admin_dashboard")
