from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("contacts/", views.contact_list, name="contact_list"),
    path("contacts/<int:pk>/", views.contact_detail, name="contact_detail"),
    path("deals/", views.deal_list, name="deal_list"),
    path("login/", auth_views.LoginView.as_view(template_name="crm/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
