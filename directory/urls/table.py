"""
Directory Table View urls.
"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from ..models import DirectoryEntry, EntryType
from ..views import DirectoryEntryUpdateView

urlpatterns = [
    url(
        r"^$",
        ListView.as_view(
            queryset=EntryType.objects.active(),
            template_name="directory/table/entrytype_list.html",
        ),
        name="directory-table-type-list",
    ),
    url(
        r"^all/$",
        ListView.as_view(
            queryset=DirectoryEntry.objects.active(),
            template_name="directory/table/directoryentry_list.html",
        ),
        name="directory-table-entry-list",
    ),
    url(
        r"^entry/(?P<pk>[\d]+)/update/$",
        login_required(
            DirectoryEntryUpdateView.as_view(
                template_name="directory/table/directoryentry_form.html"
            )
        ),
        name="directory-table-entry-update",
    ),
    url(
        r"^(?P<slug>[\w-]+)/$",
        DetailView.as_view(
            queryset=EntryType.objects.active().prefetch_related("directoryentry_set"),
            template_name="directory/table/entrytype_detail.html",
        ),
        name="directory-table-type-detail",
    ),
]
