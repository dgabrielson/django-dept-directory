"""
Utility function to allow to different person records to be merged.
"""
###############################################################

from __future__ import print_function, unicode_literals

from django.contrib.admin.utils import NestedObjects


###############################################################
"""
Compute the Damerau-Levenshtein distance between two given
strings (s1 and s2).

Reference: https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
Source: https://www.guyrutenberg.com/2008/12/15/damerau-levenshtein-distance-in-python/
Date retrieved: 2016-Sept-20
"""


def damerau_levenshtein_distance(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # deletion
                d[(i, j - 1)] + 1,  # insertion
                d[(i - 1, j - 1)] + cost,  # substitution
            )
            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition

    return d[lenstr1 - 1, lenstr2 - 1]


###############################################################


def name_check(p1, p2):
    """
    Returns a percentage difference between the names of two people
    """
    d = damerau_levenshtein_distance(p1.cn, p2.cn)
    n = min([len(p1.cn), len(p2.cn)])
    return float(d) / float(n)


###############################################################


def merge_people(
    p1_pk,
    p2_pk,
    santiy_check_cn=True,
    name_check_threshold=0.35,
    overwrite_p1=False,
    delete_p2=True,
    using=None,
    commit=True,
    verbosity=0,
):
    """
    Merge values of ``p2`` into ``p1``, and (usually) delete ``p2``.
    """

    def _get_person(pk_or_obj):
        from ..models import Person

        if isinstance(pk_or_obj, Person):
            obj = pk_or_obj
            pk = obj.pk
            qs = Person.objects.filter(pk=pk)
        else:
            pk = pk_or_obj
            qs = Person.objects.filter(pk=pk)
            obj = qs.get()
        return pk, obj, qs

    if using is None:
        using = "default"

    pk1, obj1, qs1 = _get_person(p1_pk)
    pk2, obj2, qs2 = _get_person(p2_pk)

    if verbosity > 0:
        print("Merging {} [{}] -> {} [{}]".format(obj2, pk2, obj1, pk1))

    if santiy_check_cn:
        d = name_check(obj1, obj2)
        if verbosity > 2:
            print("Name check difference = {}".format(d))
        if d > name_check_threshold:
            raise ValueError(
                "These two people have dis-similar names, refusing to merge"
            )
        if verbosity > 2:
            print("Passed name check")
    elif verbosity > 2:
        print("Skipped name check")

    if verbosity > 2:
        print(":: Updated related objects ::")
    # set related objects from obj2 to obj1::
    while True:
        # continue to recollect each object since updating this
        #   can have side effects.
        c2 = NestedObjects(using=using)
        c2.collect(qs2)
        if obj2 not in c2.edges:
            break
        o = c2.edges[obj2][0]  # list of subobject of obj to modify, do the first one
        if verbosity > 2:
            print("{}: {}".format(o._meta.verbose_name, o))
        # f_list is the list of field objects in o that point back to obj2
        f_list = [f for f in o._meta.fields if f.rel and f.rel.to == obj2._meta.model]
        for f in f_list:
            if verbosity > 1:
                msg = "{}.{} updated".format(o._meta.verbose_name, f.name)
                if verbosity > 2:
                    msg += " :: {} -> {}".format(obj2, obj1)
                print(msg)
            setattr(o, f.name, obj1)
        if commit:
            o.save(using=using)

    if verbosity > 2:
        print(":: Updated local fields objects ::")

    # set attributes on the obj1::
    for f_name in [f.name for f in obj1._meta.fields if f.rel is None]:
        if f_name in ["id", "created", "modified"]:
            continue
        value1 = getattr(obj1, f_name)
        if overwrite_p1 or not value1:
            value2 = getattr(obj2, f_name)
            if verbosity > 1:
                msg = ".{} updated".format(f_name)
                if verbosity > 2:
                    msg += " :: {!r} -> {!r}".format(value1, value2)
                print(msg)
            if f_name == "slug" and value2 and not delete_p2:
                print(
                    'Will not update destination slug field:: value "{}", as this would violate uniqueness'.format(
                        value2
                    )
                )
            else:
                setattr(obj1, f_name, value2)
    if commit:
        # delete p2, if asked.
        if delete_p2:
            obj2.delete(using=using)
        obj1.save(using=using)


###############################################################
