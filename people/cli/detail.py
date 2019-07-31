#######################
from __future__ import print_function, unicode_literals

from people.models import Person

#######################

HELP_TEXT = "Get detail on a person, including contact info"
DJANGO_COMMAND = "main"
USE_ARGPARSE = True
OPTION_LIST = (
    (["person_pk"], dict(nargs="+", help="Primary key of person to get details for")),
)
ARGS_USAGE = "pk [pk [...]]"


def print_object(obj):
    print(obj.__class__.__name__ + "\t" + "{}".format(obj))
    fields = [f.name for f in obj.__class__._meta.fields]
    for f in fields:
        print("\t" + f + "\t" + "{}".format(getattr(obj, f)))


def main(options, args):
    for pk in options["person_pk"]:
        person = Person.objects.get(pk=pk)
        print_object(person)
        print(
            "\t"
            + "flags"
            + "\t"
            + ",".join(["{}".format(f.slug) for f in person.flags.all()])
        )
        # related_sets = [ attr for attr in dir(person) if attr.endswith('_set')]
        related_sets = ["phonenumber_set", "emailaddress_set", "streetaddress_set"]
        for attr in related_sets:
            related = getattr(person, attr)
            for obj in related.all():
                print_object(obj)
        print()
