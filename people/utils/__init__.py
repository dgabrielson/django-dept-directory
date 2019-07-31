"""
Some utility functions for the people application.
"""
#######################
from __future__ import print_function, unicode_literals

from django.contrib.auth import get_user_model

from .. import conf

#######################
#######################################################################


SN_BIAS = conf.get("name_guess:sn_bias")
SN_MARK_LIST = conf.get("name_guess:sn_mark_list")

#######################################################################


def name_guess_helper(cn, given_name, sn, sn_bias=SN_BIAS, sn_mark_list=SN_MARK_LIST):
    """
    This is a reference implementation of the name guess helper function.
    It *must* take cn, given_name, and sn as arguments, and the assumption
    is that given_name and/or sn *may* be None, in which case, do the guess work.
    """
    result = {"cn": cn, "sn": sn, "given_name": given_name}
    if given_name is not None and sn is not None:
        pass

    # cn is usually of the form given_name + ' ' + sn
    if given_name is None and sn is not None:
        result["given_name"] = " ".join(cn.replace(sn, "").split()).strip()

    if given_name is not None and sn is None:
        result["sn"] = " ".join(cn.replace(given_name, "").split()).strip()

    if given_name is None and sn is None:
        guessed = False
        # watch out for names like van.. de.. del.. di..
        for sn_mark in sn_mark_list:
            if sn_mark in cn.lower():
                p = cn.lower().find(sn_mark)
                if p != -1:
                    result["given_name"] = cn[:p].strip()
                    result["sn"] = cn[p:].strip()
                    guessed = True
                    break
        # default: anglo bias: one sn, last part of cn.
        if not guessed:
            parts = cn.split()
            while True:
                if len(parts) > sn_bias:
                    result["given_name"] = " ".join(parts[:-sn_bias]).strip()
                    result["sn"] = " ".join(parts[-sn_bias:]).strip()
                    break
                if len(parts) == 1:  # a degenerate edge case.
                    result["given_name"] = parts[0]
                    result["sn"] = parts[0]
                    break
                sn_bias -= 1
                assert sn_bias != 0, (
                    "bad name input for guess_name_helper! (parts = %r)" % parts
                )

    return result


#######################################################################


def safe_user2person(user):
    """
    Safely map user object to person object.  Return None if DNE.
    """
    from ..models import Person

    try:
        return Person.objects.get_by_user(user)
    except Person.DoesNotExist:
        return None


################################################################


def safe_person2user(person):
    """
    Safely map person object to user object.  Return None if DNE.
    """
    UserModel = get_user_model()

    try:
        return person.get_user()
    except UserModel.DoesNotExist:
        return None


################################################################


def get_person_user_pair(person=None, user=None):
    """
    Safely get a person/username pair.
    """
    if person is None and user is None:
        assert False, "You must specify either a person or a user"
    if person is not None and user is None:
        from ..models import Person

        assert isinstance(person, Person)
        if person.username:
            user = safe_person2user(person)
    if person is None and user is not None:
        UserModel = get_user_model()
        assert isinstance(user, UserModel)
        person = safe_user2person(user)
    return person, user


################################################################


def person2user_name(person, user):
    """
    Given a person and a user object, apply the person name to the user.
    """
    changed = False
    if person.sync_name:
        for src_field_name in ["sn", "given_name", "cn"]:
            dst_field_name = conf.get(
                "sync:person:user-name:{0}".format(src_field_name)
            )
            if dst_field_name is None:
                continue
            value = getattr(person, src_field_name)
            dst_field = getattr(user, dst_field_name)
            if not callable(dst_field):
                old_value = getattr(user, dst_field_name)
                if old_value != value:
                    changed = True
                    setattr(user, dst_field_name, value)
    return changed


################################################################


def person2user_email(person, user):
    """
    Given a person and a user object, apply the person preferred email 
    address to the user.
    """

    def get_address(emailaddress_list):
        """
        The list will have at least one element.
        """
        for email in emailaddress_list:
            if email.preferred:
                return email.address
        if emailaddress_list.exists():
            return emailaddress_list[0].address

    # end get_address()

    emailaddress_list = person.emailaddress_set.active()
    changed = False
    address = get_address(emailaddress_list)
    if address is not None and user.email != address:
        user.email = address
        changed = True
    return changed


################################################################


def user2person_name(person, user):
    """
    Given a person and a user object, apply the person name to the user.
    """
    changed = False
    if person.sync_name:
        for dst_field_name in ["sn", "given_name", "cn"]:
            src_field_name = conf.get(
                "sync:person:user-name:{0}".format(dst_field_name)
            )
            if src_field_name is None:
                continue
            value = getattr(user, src_field_name)
            if callable(value):
                value = value()
            old_value = getattr(person, dst_field_name)
            if old_value != value:
                setattr(person, dst_field_name, value)
                changed = True
    return changed


################################################################
