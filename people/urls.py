"""
Url patterns for the people application, primarly to be used
for verifying email
"""
from django.conf.urls import url

from . import views
from .models import EmailConfirmation
from .views import admin as views_admin

urlpatterns = [
    url(r"^$", views.profile_detail, name="people-person-detail"),
    url(
        r"^verify-me/(?P<pk>\d+)/$",
        views.request_confirmation_email,
        name="people-verify-email",
    ),
    url(
        r"^confirm-email/" + EmailConfirmation.VERIFIED + "/$",
        views.already_verified,
        name="people-email-already-verified",
    ),
    url(
        r"^confirm-email/(?P<slug>[\w-]+)/$",
        views.confirm_email,
        name="people-email-confirmed",
    ),
    # administrative functions -- always restricted
    url(r"^_list/$", views_admin.person_list, name="people-admin-person-list"),
    url(r"^_new/$", views_admin.person_create, name="people-admin-person-create"),
    url(
        r"^_update/(?P<pk>[\d]+)/$",
        views_admin.person_update,
        name="people-admin-person-update",
    ),
    url(
        r"^_detail/(?P<pk>[\d]+)/$",
        views_admin.person_detail,
        name="people-admin-person-detail",
    ),
]
