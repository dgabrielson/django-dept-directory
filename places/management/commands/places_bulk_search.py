#######################
from __future__ import print_function, unicode_literals

import sys

from django.core.management.base import BaseCommand, CommandError

from ...models import ClassRoom

#######################
## https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
################################################################

#######################################################################

#######################################################################


class Command(BaseCommand):
    help = "Search for  {{ app_name|title }}Model objects"

    def add_arguments(self, parser):
        """
        Add arguments to the command.
        """
        parser.add_argument(
            "--no-detail",
            action="store_false",
            dest="show-detail",
            default=True,
            help="Show only the pk result vector",
        )

    # When you are using management commands and wish to provide console output,
    # you should write to self.stdout and self.stderr, instead of printing to
    # stdout and stderr directly. By using these proxies, it becomes much easier
    # to test your custom command. Note also that you don't need to end messages
    # with a newline character, it will be added automatically, unless you
    # specify the ``ending`` parameter to write()

    def handle(self, *args, **options):
        """
        Do the thing!
        """
        self.stdout.write(
            "Enter rooms to search for.  End with CTRL+D on a line by itself.\n\n"
        )
        txt = sys.stdin.read().strip()
        room_l = txt.split("\n")
        room_m = []
        for r in room_l:
            obj = list(ClassRoom.objects.search(r))[-1]
            room_m.append(obj)
            if options["show-detail"] or options["verbosity"] > 1:
                self.stdout.write(self.style.SUCCESS("{}\t{}".format(obj.pk, obj)))

        room_v = ",".join([str(obj.pk) for obj in room_m])
        self.stdout.write(room_v)


#######################################################################
