"""
Views for the directory application.
"""

from django.contrib import messages
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from latex.djangoviews import LaTeX_ListView

from . import conf
from .forms import DirectoryEntryForm
from .models import DirectoryEntry, EntryType

# #############################################################


def forbidden_response(request, content):
    try:
        resp = render(request, "403.html", {"test_fail_msg": content})
        resp.status_code = 403
        return resp
    except TemplateDoesNotExist:
        return HttpResponseForbidden(content)


# #############################################################


class PrintDirectory(LaTeX_ListView):
    """
    Produce the pdf for semester schedules.
    Note that this view is used by the admin interface.
    """

    queryset = EntryType.objects.active()
    template_name = "directory/print/directory.tex"
    as_attachment = False
    context_object_name = "directory_list"

    def get_queryset(self):
        """
        Get the actual queryset.
        """
        if "pk" in self.request.GET:
            selected = self.request.GET.getlist("pk")
            return self.queryset.filter(pk__in=selected)
        else:
            return self.queryset

    def get_context_data(self, *args, **kwargs):
        """
        Augment the context.
        """
        context = super(PrintDirectory, self).get_context_data(*args, **kwargs)
        context.update(conf.get("print_context"))
        return context


# #############################################################


class ByPersonListView(ListView):
    """
    List all the individuals that have a directory entry.
    """

    queryset = DirectoryEntry.objects.person_list()
    template_name = "directory/person_list.html"


by_person_list = ByPersonListView.as_view()

# #############################################################


class ByPersonDetailView(DetailView):
    """
    List the directory entries for a particular person.
    """

    queryset = DirectoryEntry.objects.person_list()
    template_name = "directory/person_detail.html"


by_person_detail = ByPersonDetailView.as_view()

# #############################################################


class DirectoryEntryUpdateView(UpdateView):
    """
    Update a directory entry
    """

    form_class = DirectoryEntryForm
    queryset = DirectoryEntry.objects.active()

    def permission_check(self, request):
        """
        Check permissions beyond simple login_required.
        """
        if request.user.is_superuser:
            return True
        if request.user.has_perm("directory.change_directoryentry"):
            return True
        if self.object.person is None:
            return False
        if self.object.person.slug is None:
            return False
        return request.user.username == self.object.person.username

    def dispatch(self, request, *args, **kwargs):
        """
        Special dispatch handling -- extra permission check and class data.
        """
        # core dispatch setup
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.object = self.get_object()  # we need this for permission check
        # extra permission check
        if not self.permission_check(request):
            return forbidden_response(
                request, "You do not have permission to update this entry."
            )
        # actual dispatch
        return super(DirectoryEntryUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        Do this as a class method to post the success message.
        """
        msg = "Directory entry successfully updated."
        messages.success(self.request, msg, fail_silently=True)
        return reverse(
            "directory-by-person-detail", kwargs={"slug": self.object.person.slug}
        )


# #############################################################
