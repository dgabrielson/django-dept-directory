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
            template_name="directory/visual_1col/entrytype_list.html",
        ),
        name="directory-visual-1col-type-list",
    ),
    url(
        r"^all/$",
        ListView.as_view(
            queryset=DirectoryEntry.objects.active(),
            template_name="directory/visual_1col/directoryentry_list.html",
        ),
        name="directory-visual-1col-entry-list",
    ),
    url(
        r"^entry/(?P<pk>[\d]+)/update/$",
        login_required(
            DirectoryEntryUpdateView.as_view(
                template_name="directory/visual_1col/directoryentry_form.html"
            )
        ),
        name="directory-visual-1col-entry-update",
    ),
    url(
        r"^(?P<slug>[\w-]+)/$",
        DetailView.as_view(
            queryset=EntryType.objects.active().prefetch_related("directoryentry_set"),
            template_name="directory/visual_1col/entrytype_detail.html",
        ),
        name="directory-visual-1col-type-detail",
    ),
]
