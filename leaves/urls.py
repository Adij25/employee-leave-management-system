from django.urls import path
from . import views

app_name = "leaves"
urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("apply/", views.apply_leave, name="apply_leave"),
    path("history/", views.leave_history, name="leave_history"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("review/<int:pk>/<str:action>/", views.review_leave, name="review_leave"),
]
