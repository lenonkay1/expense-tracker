from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("add/", views.add_expense, name="add_expense"),
    path("edit/<int:expense_id>/", views.edit_expense, name="edit_expense"),
    path("delete/<int:expense_id>/", views.delete_expense, name="delete_expense"),
    path("register/", views.register_page, name="register"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("profile/", views.profile_settings, name="profile"),
    path("export/csv/", views.export_csv, name="export_csv"),
    path("export/pdf/", views.export_pdf, name="export_pdf"),
    path("add-income/", views.add_income, name="add_income"),
]
