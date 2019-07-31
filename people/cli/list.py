"""
List the people.

Example Alumni Report:
python manage.py people list --flags alumni -f emailaddress_set.active.0,graduatestudent_set.alumni_filter.0.get_program_display,graduatestudent_set.alumni_filter.0.graduation_date | cut -f 2-5 | sed 's/Failed lookup for \[0\]//' > ~/Desktop/alumni_report.txt
# .. the resulting tab delimited file can be easily converted to a spreadsheet.


"""
#######################
from __future__ import print_function, unicode_literals

from ..models import Person as Model
from . import resolve_fields

#######################
#######################################################################
#######################################################################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
USE_ARGPARSE = True
OPTION_LIST = (
    (
        ["-f", "--fields"],
        dict(
            dest="field_list",
            help="Specify a comma delimited list of fields to include, e.g., -f PROVIDE,EXAMPLE",
        ),
    ),
    (
        ["--flags"],
        dict(help="Specify a comma delimited list of flag slugs to filter the list"),
    ),
)

#######################################################################

#######################################################################


def main(options, args):

    queryset = Model.objects.active()
    if options["flags"]:
        queryset = queryset.filter(flags__slug__in=options["flags"].split(","))

    for item in queryset.iterator():
        value_list = ["{}".format(item.pk), "{}".format(item)]
        if options["field_list"]:
            value_list += resolve_fields(item, options["field_list"].split(","))
        print("\t".join(value_list))


#######################################################################
