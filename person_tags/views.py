"""
Custom views for the Person_Tags application
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from people.models import Person

from .forms import PersonForm, PersonTagForm, get_persontaggedentry_formset_class
from .models import PersonTag, PersonTaggedEntry

## ######################################################### ##


def permission_check(request, person):
    if request.user.is_superuser:
        return True
    if request.user.has_perm("person_tags.change_persontaggedentry"):
        return True
    if person.slug is None:
        return False
    return request.user.username == person.username


def forbidden_response(request, content):
    try:
        resp = render(request, "403.html", {"test_fail_msg": content})
        resp.status_code = 403
        return resp
    except TemplateDoesNotExist:
        return HttpResponseForbidden(content)


class PersonTaggedEntryUpdateView(UpdateView):
    """
    Class for updating person tagged entries.
    """

    form_class = PersonForm
    formset_initial = [{"active": True, "ordering": 10}]
    formset_prefix = None
    queryset = Person.objects.active()
    template_name = "person_tags/persontaggedentry_form.html"

    def get_formset_class(self):
        kwargs = {"fields": ("active", "tag", "ordering"), "extra": 1}
        return get_persontaggedentry_formset_class(**kwargs)

    def get_formset_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.formset_initial.copy()

    def get_formset_prefix(self):
        """
        Returns the prefix to use for forms on this view
        """
        return self.formset_prefix

    def get_formset_kwargs(self):
        kwargs = {
            "initial": self.get_formset_initial(),
            "prefix": self.get_formset_prefix(),
            "instance": self.object,
        }

        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST, "files": self.request.FILES})
        return kwargs

    def get_formset(self, formset_class=None):
        """
        Returns an instance of the form to be used in this view.
        """
        if formset_class is None:
            formset_class = self.get_formset_class()
        return formset_class(**self.get_formset_kwargs())

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        context = super(PersonTaggedEntryUpdateView, self).get_context_data(**kwargs)
        if "formset" not in context:
            context["formset"] = self.get_formset()
        return context

    def form_valid(self, form, formset):
        """
        If the form is valid, save the associated model.
        """
        result = super(PersonTaggedEntryUpdateView, self).form_valid(form)
        formset.save()
        return result

    def form_invalid(self, form, formset):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.object = self.get_object()
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)


person_tagged_entry_update = login_required(PersonTaggedEntryUpdateView.as_view())

## ######################################################### ##


class PersonTagCreateView(CreateView):
    """
    Class for creating new tags
    """

    form_class = PersonTagForm
    queryset = PersonTag.objects.all()
    template_name = "person_tags/persontag_form.html"

    def permission_check(self, request):
        """
        Check permissions beyond simple login_required.
        """
        if request.user.is_superuser:
            return True
        if request.user.has_perm("person_tags.create_persontag"):
            return True
        if self.person is None:
            return False
        if self.person.slug is None:
            return False
        return request.user.username == self.person.username

    def dispatch(self, request, *args, **kwargs):
        """
        Special dispatch handling -- extra permission check and class data.
        """
        self.person = None
        slug = self.kwargs.get("slug", None)
        if slug is None:
            try:
                self.person = Person.objects.get_by_user(request.user)
            except Person.DoesNotExist:
                pass
        else:
            try:
                self.person = Person.objects.get(active=True, slug=slug)
            except Person.DoesNotExist:
                pass
        if not self.permission_check(request):
            return forbidden_response(
                request, "You do not have permission to create a tag."
            )
        return super(PersonTagCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Insert the loaded person into the view context.
        """
        # Call the base implementation first to get a context
        context = super(PersonTagCreateView, self).get_context_data(**kwargs)
        context["person"] = self.person
        return context

    def form_valid(self, *args, **kwargs):
        result = super(PersonTagCreateView, self).form_valid(*args, **kwargs)
        # Also create a PersonTaggedEntry for the new tag.
        PersonTaggedEntry.objects.get_or_create(person=self.person, tag=self.object)
        return result

    def get_success_url(self):
        """
        Do this as a class method to post the success message.
        """
        msg = "New tag successfully created."
        messages.success(self.request, msg, fail_silently=True)
        slug = self.kwargs.get("slug", None)
        if slug is None:
            return reverse("persontag-persontag-create-general")
        else:
            return reverse("persontag-persontag-create", kwargs={"slug": slug})


person_tag_create = login_required(PersonTagCreateView.as_view())

## ######################################################### ##
