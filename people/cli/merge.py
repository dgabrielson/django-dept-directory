from __future__ import print_function, unicode_literals

import sys

HELP_TEXT = "Merge two people, and remove "
DJANGO_COMMAND = "main"
USE_ARGPARSE = True
OPTION_LIST = (
    (["src_pk"], {"help": "Source person for merge, required"}),
    (["dst_pk"], {"help": "Destination person for merge, required"}),
    (
        ["--noinput"],
        {"help": "Suppress regular confirmation check", "action": "store_true"},
    ),
)
ARGS_USAGE = "dst_pk"


def main(options, args):
    verbosity = int(options["verbosity"])
    from ..utils.merge import merge_people
    from ..models import Person

    if not options["noinput"]:
        src = Person.objects.get(pk=options["src_pk"])
        dst = Person.objects.get(pk=options["dst_pk"])
        sys.stdout.write(
            'Are you sure you want to merge "{}" into "{}"? [y/N] '.format(src, dst),
            ending="",
        )
        confirm = input()
        if not confirm.lower() == "y":
            sys.exit(0)

    merge_people(options["dst_pk"], options["src_pk"], verbosity=verbosity)
