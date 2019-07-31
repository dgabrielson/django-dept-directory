#######################
from __future__ import print_function, unicode_literals

from ..models import EmailConfirmation

#######################

HELP_TEXT = "Cleanup email verifications"
DJANGO_COMMAND = "main"
USE_ARGPARSE = True
OPTION_LIST = ()


def main(options, args):

    if args:
        print("This management command takes no arguments.")

    EmailConfirmation.objects.delete_expired()
