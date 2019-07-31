#######################
from __future__ import print_function, unicode_literals

from places.models import ClassRoom, Office, Room

#######################

HELP_TEXT = "Search for rooms"
DJANGO_COMMAND = "main"
OPTION_LIST = ()
ARGS_USAGE = "[search terms]"


def room_type(room):
    try:
        room.office
        return "office"
    except Office.DoesNotExist:
        pass
    try:
        room.classroom
        return "classroom"
    except ClassRoom.DoesNotExist:
        pass


def main(options, args):
    for room in Room.objects.search(*args):
        result = "{}".format(room.pk) + "\t" + "{}".format(room)
        t = room_type(room)
        if t:
            result += "\t" + t
        print(result)
