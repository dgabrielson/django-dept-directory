#######################
from __future__ import print_function, unicode_literals

from people.models import Person

from . import detail

#######################

HELP_TEXT = "Search"
DJANGO_COMMAND = "main"
USE_ARGPARSE = True
OPTION_LIST = (
    (
        ["--no-detail"],
        dict(
            action="store_false",
            dest="show-detail",
            default=True,
            help="By default, when only one result is returned, details will be printed also.  Giving this flag supresses this behaviour",
        ),
    ),
    (["term"], {"nargs": "+", "help": "Search constraints"}),
)
ARGS_USAGE = "[search terms]"

Model = Person


def main(options, args):
    obj_list = Model.objects.search(options["term"])
    if options["show-detail"] and obj_list.count() == 1:
        obj = obj_list.get()
        detail.main({"person_pk": obj.pk}, [obj.pk])
    else:
        for obj in obj_list:
            print("{}".format(obj.pk) + "\t" + "{}".format(obj))
