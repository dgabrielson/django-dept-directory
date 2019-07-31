#########################################################################

from django.apps import AppConfig
from django.db import models
from django.utils.translation import ugettext_lazy as _

#########################################################################


class DirectoryConfig(AppConfig):
    name = "directory"
    verbose_name = _("Directory")

    def ready(self):
        """
        Any app specific startup code, e.g., register signals,
        should go here.
        """
        from . import conf, signals

        if conf.get("signals:entrytypes-personflags"):
            from people.models import Person, PersonFlag

            # Register configured synchronization signal handlers
            from .models import EntryType, DirectoryEntry

            # There *may* be circumstances where we need full synchronization
            if conf.get("signals:entrytypes-personflags:personflag-fwd-on"):
                models.signals.pre_save.connect(
                    signals.personflag_pre_save_to_entrytype, sender=PersonFlag
                )
                models.signals.post_delete.connect(
                    signals.personflag_post_delete_entrytype_delete, sender=PersonFlag
                )
            models.signals.pre_save.connect(
                signals.entrytype_pre_save_to_personflag, sender=EntryType
            )
            models.signals.post_delete.connect(
                signals.entrytype_post_delete_personflag_delete, sender=EntryType
            )
            models.signals.m2m_changed.connect(
                signals.person_flags_m2m_changed_handler, sender=Person.flags.through
            )
            models.signals.pre_save.connect(
                signals.directoryentry_pre_save, sender=DirectoryEntry
            )
            models.signals.post_delete.connect(
                signals.directoryentry_post_delete, sender=DirectoryEntry
            )


#########################################################################
