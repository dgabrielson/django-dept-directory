#########################################################################

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

#########################################################################


class PersonTagsConfig(AppConfig):
    name = "person_tags"
    verbose_name = _("Person Tags")

    def ready(self):
        """
        Any app specific startup code, e.g., register signals,
        should go here.
        """


#########################################################################
