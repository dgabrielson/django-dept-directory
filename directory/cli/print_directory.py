#!/usr/bin/env python
"""
Generate a printable directory.
Default behaviour is to preview the generated PDF.
"""
#######################
from __future__ import print_function, unicode_literals

import sys
import time
from optparse import make_option

from directory.models import DirectoryEntry, EntryType
from django.template import Context, Template
from django.template.loader import render_to_string
from latex import LaTeX_Document

from .. import conf

#######################

#############################################################

DJANGO_COMMAND = "main"
HELP_TEXT = __doc__.strip()
OPTION_LIST = (
    make_option(
        "--pdf",
        dest="pdf",
        action="store_true",
        help="Output the PDF datastream to stdout",
    ),
    make_option(
        "--tex",
        dest="tex",
        action="store_true",
        help="Output the LaTeX source to stdout",
    ),
)

#############################################################

TEMPLATE = "directory/print/directory.tex"

# extra_context = conf.get('extra_context')

#############################################################


def main(options, args):
    d = LaTeX_Document()
    context = {"directory_list": EntryType.objects.active()}
    #    context.update(extra_context)
    src = render_to_string(TEMPLATE, context)

    d.set_full_src(src)

    if options["pdf"] and options["tex"]:
        print("You cannot use both --pdf and --tex")
        sys.exit(1)
    elif options["pdf"]:
        sys.stdout.write(d.pdf_data())
    elif options["tex"]:
        sys.stdout.write(str(d))
        if sys.stdout.isatty() and not str(d).endswith("\n"):
            print
    else:
        d.preview()
        time.sleep(0.5)  # give preview a chance to load before cleanup
