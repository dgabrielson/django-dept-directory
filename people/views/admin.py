"""
Views for the person application,

Primarly used for automatic email confirmations.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from ..forms import AdminPersonForm
from ..models import Person

# #############################################################


def forbidden_response(request, content):
    try:
        resp = render(request, "403.html", {"test_fail_msg": content})
        resp.status_code = 403
        return resp
    except TemplateDoesNotExist:
        return HttpResponseForbidden(content)


# #############################################################

###############################################################


class AdminPersonMixin(object):
    """
    Mixin for all AdminPerson views
    """

    queryset = Person.objects.filter(active=True)
    permission_fail_msg = "You do not have permission to do this."

    def permission_check(self, request):
        """
        Subclasses may extend this further.
        Check permissions beyond simple login_required.

        NOTE: Make no assumptions about the state of the view class instance.
            (This check occurs *very* early.)
        """
        # even admin viewing requires edit permissions.
        if request.user.has_perm("people.change_person"):
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        """
        Special dispatch handling -- permissions checks
        """
        # extra permission check
        if not self.permission_check(request):
            return forbidden_response(request, self.permission_fail_msg)
        # actual dispatch -- note we call the base view directly
        return View.dispatch(self, request, *args, **kwargs)


###############################################################


class AdminPersonFormMixin(AdminPersonMixin):
    """
    Mixin for common code for second-face admin forms.
    """

    form_class = AdminPersonForm
    success_message = None

    def get_success_message(self):
        if self.success_message:
            return self.success_message
        raise ImproperlyConfigured(
            "No success message.  Either override the "
            + "get_success_message method or set the success_message "
            + "attribute in your Form class."
        )

    def get_success_url(self):
        """
        Do this as a class method to post the success message.
        """
        msg = self.get_success_message()
        messages.success(self.request, msg, fail_silently=True)
        return reverse("people-admin-person-detail", kwargs={"pk": self.object.pk})


###############################################################


class PersonListView(AdminPersonMixin, ListView):
    """
    Provide a paginated list of people.
    """

    paginate_by = 100
    permission_fail_msg = "You do not have permission to view the person list."

    def get_queryset(self, *args, **kwargs):
        """
        Get a restricted queryset if there is a search term,
        otherwise, get the default queryset.
        """
        if "q" in self.request.GET:
            query = self.request.GET["q"]
            return self.queryset.search(query)
        return self.queryset


person_list = login_required(PersonListView.as_view())

###############################################################


class PersonDetailView(AdminPersonMixin, DetailView):
    """
    Provide detail on a single person
    """

    permission_fail_msg = "You do not have permission to view person details."


person_detail = login_required(PersonDetailView.as_view())

###############################################################


class PersonCreateView(AdminPersonFormMixin, CreateView):
    """
    Create a new person
    """

    template_name = "people/person_form.html"
    permission_fail_msg = "You do not have permission to create a new person."

    def permission_check(self, request):
        """
        Subclasses may extend this further.
        Check permissions beyond simple login_required.

        NOTE: Make no assumptions about the state of the view class instance.
            (This check occurs *very* early.)
        """
        if request.user.has_perm("people.add_person"):
            return True
        return False

    def get_success_message(self):
        return "The person {self.object} has been created".format(self=self)


person_create = login_required(PersonCreateView.as_view())

###############################################################


class PersonUpdateView(AdminPersonFormMixin, UpdateView):
    """
    Update an existing person
    """

    permission_fail_msg = "You do not have permission to update an existing person."

    def get_success_message(self):
        return "The person {self.object} has been updated".format(self=self)


person_update = login_required(PersonUpdateView.as_view())

###############################################################
