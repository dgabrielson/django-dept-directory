#######################
from __future__ import print_function, unicode_literals

from places.models import ClassRoom, Office, Room

from .search import room_type

#######################

HELP_TEXT = "List rooms"
DJANGO_COMMAND = "main"
USE_ARGPARSE = True
OPTION_LIST = (
    (
        ["--classroom"],
        dict(
            dest="classroom",
            action="store_true",
            default=False,
            help="List only classrooms",
        ),
    ),
    (
        ["--office"],
        dict(
            dest="office", action="store_true", default=False, help="List only offices"
        ),
    ),
)


def get_queryset(options):
    if options["classroom"]:
        return ClassRoom.objects.active()
    if options["office"]:
        return Office.objects.active()
    return Room.objects.active()


def display(options, room):
    result = "{}".format(room.pk) + "\t" + "{}".format(room)

    if options["classroom"]:
        result += "\t" + "{}".format(room.capacity)

    elif options["office"]:
        result += "\t" + "{}".format(room.phone_number)

    else:
        t = room_type(room)
        if t:
            result += "\t" + t
    return result


def main(options, args):
    for room in get_queryset(options):
        print(display(options, room))
