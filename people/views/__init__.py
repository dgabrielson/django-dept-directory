"""
Views for the person application,

Primarly used for automatic email confirmations.
"""

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from ..models import EmailAddress, EmailConfirmation, Person

###############################################################


class RequestConfirmationEmail_View(DetailView):
    """
    Send out a confirmation email request.
    """

    queryset = EmailAddress.objects.filter(active=True)
    redirect_field_name = "next"

    def get(self, request, *args, **kwargs):
        """
        Call the base implementation first to get a valid response
        """
        response = super(self.__class__, self).get(request, *args, **kwargs)
        username = request.user.username
        try:
            person = Person.objects.get(active=True, username=username)
        except Person.DoesNotExist:
            raise Http404
        # ensure that this person owns this address.
        if person != self.object.person:
            raise Http404

        # passed all the checks. Do it!
        redirect_to = self.request.GET.get(self.redirect_field_name, "")
        EmailConfirmation.objects.start_verification(
            self.object, redirect_url=redirect_to
        )

        return response


request_confirmation_email = login_required(RequestConfirmationEmail_View.as_view())

###############################################################


class ConfirmEmail_View(DetailView):
    """
    Actually confirm a given email address.
    Requires the confirmation key, sent via email.
    """

    slug_field = "key"
    queryset = EmailConfirmation.objects.filter(active=True)

    def get(self, request, *args, **kwargs):
        """
        Call the base implementation first to get a valid response
        """
        response = super(ConfirmEmail_View, self).get(request, *args, **kwargs)

        # NOTE: email confirmations can occur without local users.
        # so this is *not* done!
        # username = request.user.username
        # try:
        #     person = Person.objects.get(active=True, username=username)
        # except Person.DoesNotExist:
        #     raise Http404
        # # ensure that this person owns this address.
        # if person != self.object.email.person:
        #     raise Http404

        # inject the email and the person into the session, for later use.
        request.session["confirm_email_pk"] = self.object.email.pk

        # passed all the checks. Do it!
        self.object.set_verified()
        if self.object.redirect_url:
            return HttpResponseRedirect(self.object.redirect_url)

        return response


confirm_email = ConfirmEmail_View.as_view()

###############################################################


class AlreadyVerifiedView(TemplateView):
    template_name = "people/emailconfirmation_already_verified.html"


already_verified = AlreadyVerifiedView.as_view()

###############################################################


class Profile_DetailView(DetailView):
    """
    Display information about the person logged in.
    """

    queryset = Person.objects.filter(active=True, username__isnull=False)
    template_name = "people/person_profile.html"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        username = self.request.user.username
        try:
            person = queryset.get(username=username)
        except Person.DoesNotExist:
            raise Http404
        return person


profile_detail = login_required(Profile_DetailView.as_view())

###############################################################
