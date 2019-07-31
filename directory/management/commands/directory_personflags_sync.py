"""
Use this when enabling the "signals:entrytypes-personflags"
configuration option.
"""
#######################################################################

from django.core.management.base import BaseCommand, CommandError

#######################################################################


class Command(BaseCommand):
    help = " ".join(__doc__.split())

    def add_arguments(self, parser):
        """
        Add arguments to the command.
        """
        parser.add_argument(
            "--no-save", action="store_true", help="Do not save changes."
        )

    def handle(self, *args, **options):

        save = not options.get("no_save")
        verbosity = options.get("verbosity")

        from ... import conf

        if not conf.get("signals:entrytypes-personflags"):
            self.stderr.write(
                "Refusing to run because signals:entrytypes-personflags is not set"
            )
            return

        from ...models import DirectoryEntry, EntryType
        from ...signals import should_sync, entrytype_pre_save_to_personflag
        from people.models import PersonFlag

        for entrytype in EntryType.objects.all():
            if not should_sync(entrytype.slug):
                if verbosity > 2:
                    self.stderr.write("Skipping flag: {}".format(entrytype))
                continue
            if verbosity > 0:
                self.stdout.write("person flag: {}".format(entrytype))
            entrytype_pre_save_to_personflag(
                self.__class__.__name__, entrytype, raw=not save
            )

        for entry in DirectoryEntry.objects.all():
            if not should_sync(entry.type.slug):
                if verbosity > 2:
                    self.stderr.write(
                        "Skipping flag {} for person {}".format(
                            entry.type, entry.person
                        )
                    )
                continue
            flag = PersonFlag.objects.get(slug=entry.type.slug)
            if not entry.active:
                if verbosity > 0:
                    self.stdout.write(
                        "person: {} \t removing flag: {}".format(entry.person, flag)
                    )
                if save:
                    entry.person.flags.remove(flag)
            else:
                if verbosity > 0:
                    self.stdout.write(
                        "person: {} \t   adding flag: {}".format(entry.person, flag)
                    )
                if save:
                    entry.person.flags.add(flag)
