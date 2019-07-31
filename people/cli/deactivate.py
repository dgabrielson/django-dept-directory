"""
Do a cascade deactivate on a person.
"""
#######################
from __future__ import print_function, unicode_literals

from people.models import Person

#######################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
USE_ARGPARSE = True
OPTION_LIST = ()
ARGS_USAGE = "[search terms]"


def get_object_tree(obj):
    """
    Return all objects that point to this object via *_set() attributes.
    """
    result = {}

    my_key = obj.__class__.__name__
    result[my_key] = [obj, []]

    related_sets = [attr for attr in dir(obj) if attr.endswith("_set")]
    for attr in related_sets:
        related_set = getattr(obj, attr)
        # magical field introspection...
        fields = [f.name.lower() for f in related_set.model._meta.fields]
        if "active" in fields:
            for subobj in related_set.all():
                result[my_key][1].append(get_object_tree(subobj))
    return result


def confirm_deactivate(tree, level=0):
    for key in tree:
        value, subtree_list = tree[key]
        print(" " * (4 * level), key, ":", value)
        for subtree in subtree_list:
            confirm_deactivate(subtree, level + 1)
    if level == 0:
        print
        user_input = input("Are you sure you want to deactivate? [Y/n] ")
        if user_input == "Y":
            print
            return True
    return False


def do_deactivate(tree, level=0):
    """
    Deactivate all objects in the given tree.
    """
    for key in tree:
        obj, subtree_list = tree[key]
        print(" " * (4 * level), key, ":", obj, end=" ")
        if hasattr(obj, "active"):
            print("[active = False]")
            obj.active = False
        if hasattr(obj, "Active"):
            print("[Active = False]")
            obj.Active = False
        obj.save()
        for subtree in subtree_list:
            do_deactivate(subtree, level + 1)


def main(options, args):
    search = Person.objects.search(*args)

    if search.count() == 0:
        print("[!!!] no person found")
        return False

    if search.count() == 1:
        obj = search.get()
        tree = get_object_tree(obj)
        if confirm_deactivate(tree):
            do_deactivate(tree)
            return True
        return False

    if search.count() > 1:
        print("[!!!] multiple result of search. Use narrower terms.")
        return False

    # should never happen:
    assert False, "search.count() == %d" % search.count()
