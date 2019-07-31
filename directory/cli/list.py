"""
CLI list for DirectoryEntry objects.
"""
#######################
from __future__ import print_function, unicode_literals

from ..models import DirectoryEntry as Model
from . import resolve_fields

#######################
#######################################################################
#######################################################################

HELP_TEXT = "{}".format(__doc__).strip()
DJANGO_COMMAND = "main"
USE_ARGPARSE = True
OPTION_LIST = (
    (
        ["-f", "--fields"],
        dict(
            dest="field_list",
            help="Specify a comma delimited list of fields to include, e.g., -f office.note",
            default="type,office,office.phone_number,person.email",
        ),
    ),
)

# ARGS_USAGE = '...'

#######################################################################
#######################################################################

#######################################################################


def main(options, args):

    qs = Model.objects.active()
    for item in qs:
        value_list = ["{}".format(item.pk), "{}".format(item)]
        if options["field_list"]:
            value_list += resolve_fields(item, options["field_list"].split(","))
        print("\t".join(value_list))


#######################################################################
