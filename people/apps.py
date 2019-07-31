#########################################################################

from django.apps import AppConfig
from django.db import models
from django.utils.translation import ugettext_lazy as _

#########################################################################


class PeopleConfig(AppConfig):
    name = "people"
    verbose_name = _("People")

    def ready(self):
        """
        Any app specific startup code, e.g., register signals,
        should go here.
        """
        from . import conf, handlers
        from .models import Person, EmailAddress, PersonFlag

        # Register configured synchronization signal handlers
        from django.contrib.auth.models import User, Group

        # Note: bad handling with the User model / signal sender limitations...

        if conf.get("sync:person:user-name"):
            models.signals.post_save.connect(
                handlers.person_post_save_name_to_user, sender=Person
            )
            models.signals.post_save.connect(
                handlers.user_post_save_name_to_person, sender=User
            )

        if conf.get("sync:person:user:create-delete"):
            models.signals.post_save.connect(
                handlers.person_post_save_create_user, sender=Person
            )
            models.signals.post_delete.connect(
                handlers.person_post_delete_user_delete, sender=Person
            )
            models.signals.post_save.connect(
                handlers.user_post_save_create_person, sender=User
            )
            models.signals.post_delete.connect(
                handlers.user_post_delete_person_delete, sender=User
            )

        if conf.get("sync:person:user-email"):
            models.signals.post_save.connect(
                handlers.user_post_save_email_to_person, sender=User
            )
            models.signals.post_save.connect(
                handlers.emailaddress_post_save_email_to_user, sender=EmailAddress
            )

        if conf.get("sync:person-flags:user-groups"):
            models.signals.pre_save.connect(
                handlers.personflag_pre_save_to_group, sender=PersonFlag
            )
            models.signals.post_delete.connect(
                handlers.personflag_post_delete_group_delete, sender=PersonFlag
            )
            models.signals.pre_save.connect(
                handlers.group_pre_save_to_personflag, sender=Group
            )
            models.signals.post_delete.connect(
                handlers.group_post_delete_personflag_delete, sender=Group
            )
            models.signals.m2m_changed.connect(
                handlers.person_flags_m2m_changed_handler, sender=Person.flags.through
            )
            models.signals.m2m_changed.connect(
                handlers.user_groups_m2m_changed_handler, sender=User.groups.through
            )


#########################################################################
