"""
Activate in your template by putting
{% load directory_tags %}
near the top.

Available Tags:
visual_table  - restructure a list for the visual table.
cloak_email_link - create an obfuscated mailto href.
"""
import random
import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from ..models import EntryType

#####################################################################

register = template.Library()

#####################################################################


@register.filter
def visual_table(sequence, count):
    """
    Returns a new sequence suitable for use in producing the visual table

    Usage: {% for row in directory_list|visual_table:"4" %} ... {% endfor %}

    """
    try:
        count = int(count)
    except ValueError:
        raise template.TemplateSyntaxError(
            "argument to visual_table must be the number of columns in a row"
        )

    results = []
    length = len(sequence)
    n = 0
    while True:
        if n >= length:
            break
        subseq = sequence[n : n + count]
        n += count
        results.append(subseq)
        results.append(subseq)
    return results


#####################################################################


@register.filter
@stringfilter
def cloak_email_link(email, text=None, autoescape=None):
    """
    Source: http://djangosnippets.org/snippets/1284/
    Date retrieved: 2011-Apr-21

    [dcg] I have changed the filter name from 'mungify' to email_link.
    Problems: Can't email link, e.g., an image easily.

    -------------

    Template filter to hide an email address away from any sort of email
    harvester type web scrapers and so keep away from spam etc.

    The filter should be applied on a string which represents an email
    address. You can optionally give the filter a parameter which will
    represent the name of the resulting email href link. If no extra
    parameter is given the email address will be used as the href text.

    {{ email|email_link:"contact me" }} or {{ email|email_link }}

    The output is javascript which will write out the email href link in
    a way so as to not actually show the email address in the source code
    as plain text.
    """
    text = text or email

    if autoescape:
        email = conditional_escape(email)
        text = conditional_escape(text)

    emailArrayContent = ""
    textArrayContent = ""
    r = lambda c: '"' + str(ord(c)) + '",'

    for c in email:
        emailArrayContent += r(c)
    for c in text:
        textArrayContent += r(c)

    result = """<script>
                var _tyjsdf = [%s], _qplmks = [%s];
                document.write('<a href="&#x6d;&#97;&#105;&#x6c;&#000116;&#111;&#x3a;');
                for(_i=0;_i<_tyjsdf.length;_i++){document.write('&#'+_tyjsdf[_i]+';');}
                document.write('">');
                for(_i=0;_i<_qplmks.length;_i++){document.write('&#'+_qplmks[_i]+';');}
                document.write('</a>');
                </script>""" % (
        re.sub(r",$", "", emailArrayContent),
        re.sub(r",$", "", textArrayContent),
    )

    return mark_safe(result)


cloak_email_link.needs_autoescape = True

#####################################################################


@register.simple_tag(takes_context=True)
def get_directory_entrytypes(context, save_as=None, days=None, max_count=None):
    """
    {% get_directory_entrytypes %} -> qs
    {% get_directory_entrytypes 'entrytypes_qs' %}
    """
    qs = EntryType.objects.active()
    if save_as is not None:
        context[save_as] = qs
        return ""
    return qs


#####################################################################
