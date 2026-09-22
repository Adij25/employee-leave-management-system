from django.contrib import admin
from .models import LeaveRequest, EmployeeLeaveBalance, LeaveType


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "leave_type", "start_date", "end_date", "days", "status", "reviewed_by", "reviewed_at")
    list_filter = ("status", "leave_type", "start_date")
    search_fields = ("user__phone", "user__first_name", "user__last_name", "user__employee_id")
    readonly_fields = ("user", "leave_type", "start_date", "end_date", "days", "reason", "status", "applied_at", "reviewed_by", "reviewed_at")
    ordering = ("-applied_at",)

    # Leave requests are submitted by employees and reviewed only through
    # the dedicated admin dashboard. This prevents status changes from the
    # generic Django admin form.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EmployeeLeaveBalance)
class EmployeeLeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "casual", "sick", "other")
    search_fields = ("user__phone", "user__first_name", "user__last_name")


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "default_days")
    search_fields = ("name",)
