from django.conf.urls import url
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import PersonTag, PersonTaggedEntry, TagGroup
from .views import person_tag_create, person_tagged_entry_update

urlpatterns = [
    url(
        r"^$",
        ListView.as_view(
            queryset=PersonTaggedEntry.objects.default(),
            template_name="person_tags/persontaggedentry_list.html",
        ),
        name="persontag-person-list",
    ),
    url(
        r"^areas/$",
        ListView.as_view(queryset=TagGroup.objects.active()),
        name="persontag-taggroup-list",
    ),
    url(
        r"^areas/(?P<slug>[\w-]+)/$",
        DetailView.as_view(queryset=TagGroup.objects.active()),
        name="persontag-taggroup-detail",
    ),
    url(
        r"^interests/$",
        ListView.as_view(
            queryset=PersonTag.objects.tag_list(),
            template_name="person_tags/tag_list.html",
            context_object_name="tag_list",
        ),
        name="persontag-tag-list",
    ),
    url(
        r"^interests/(?P<slug>[\w-]+)/$",
        DetailView.as_view(
            queryset=PersonTag.objects.active(),
            template_name="person_tags/tag_detail.html",
            context_object_name="tag",
        ),
        name="persontag-tag-detail",
    ),
    url(
        r"^personal/(?P<slug>[\w-]+)/$",
        DetailView.as_view(
            queryset=PersonTag.objects.person_list(),
            template_name="person_tags/person_detail.html",
        ),
        name="persontag-person-detail",
    ),
    url(
        r"^personal/(?P<slug>[\w-]+)/update/$",
        person_tagged_entry_update,
        name="persontag-person-tagged-entry-update",
    ),
    url(
        r"^personal/(?P<slug>[\w-]+)/new-tag/$",
        person_tag_create,
        name="persontag-persontag-create",
    ),
    url(r"^tag/new/$", person_tag_create, name="persontag-persontag-create-general"),
]
