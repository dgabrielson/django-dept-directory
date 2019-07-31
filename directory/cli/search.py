"""
This module is here as a stub so that it can be enabled later.
Uncomment DJANGO_COMMAND when the DirectoryEntry QuerySet/Manager
gets a search method.
"""
#######################
from __future__ import print_function, unicode_literals

from optparse import make_option

from ..models import DirectoryEntry as Model
from . import detail

#######################
#######################################################################

HELP_TEXT = "Search for  DirectoryEntry objects"
# DJANGO_COMMAND = 'main'
OPTION_LIST = (
    make_option(
        "--no-detail",
        action="store_false",
        dest="show-detail",
        default=True,
        help="By default, when only one result is returned, details will be printed also.  Giving this flag supresses this behaviour",
    ),
)
ARGS_USAGE = "[search terms]"

#######################################################################

#######################################################################


def main(options, args):
    obj_list = Model.objects.search(*args)
    if options["show-detail"] and obj_list.count() == 1:
        obj = obj_list.get()
        detail.main({}, [obj.pk])
    else:
        for obj in obj_list:
            print("{}".format(obj.pk) + "\t" + "{}".format(obj))


#######################################################################
