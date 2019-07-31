#########################################################################

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

#########################################################################


class PlacesConfig(AppConfig):
    name = "places"
    verbose_name = _("Places")

    def ready(self):
        """
        Any app specific startup code, e.g., register signals,
        should go here.
        """


#########################################################################
