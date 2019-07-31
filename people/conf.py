"""
The DEFAULT configuration is loaded when the named _CONFIG dictionary
is not present in your settings.
"""

CONFIG_NAME = "PEOPLE_CONFIG"  # must be uppercase!

# from django.utils.text import slugify
#
#
# def default_person_slugify(instance):
#     if instance.slug:
#         return instance.slug
#     return slugify(instance.cn)

DEFAULT = {
    # 'permalink' provides a pluggable system for mapping person objects
    #   to a page, used by person.get_absolute_url -- this is either
    #   'None' (no personal pages) or a tuple ('named-view, arg_map)
    #   where the arg map is a callable which maps the person object
    #   into the correct arguments for the view.
    "permalink": None,
    # Default type (slug) for contact information
    "default_contact_info_type": "work",
    # The length of time (in hours) a user has from the time
    # the verification email is sent until it expires.
    "verification_timeout": 2 * 24,
    # A string or callable for guessing names with incomplete data.
    "name_guess:function": "people.utils.name_guess_helper",
    # Should slugs be created automatically, or not?
    "autoslug": False,
    # Reference implementation setting: westerners typically have a single surname
    "name_guess:sn_bias": 1,
    # Reference implementation setting: a list of surname markers, which, when
    #  found by themselves, indicate the beginning of a surname.
    #  NOTE: this list must be space-surrounded, and is case insensitive.
    "name_guess:sn_mark_list": [
        " {0} ".format(e) for e in ["van", "von", "de", "del", "di", "da", "st."]
    ],
    # The fields for the core AdminPersonForm.
    # any subset of the Person object fields can be specified.
    "admin_person_fields": ["cn", "given_name", "sn", "username"],
    # use None to show the default change list.
    "admin_person_default_query": {"q": "Search for people"},
    # Additional forms which are handled by the AdminPersonForm.
    # See person_subforms_api.txt for info on the required API.
    "extra_person_forms": ["people.forms.EmailAddressPersonSubForm"],
    # Synchronization settings:
    # Sync name changes
    "sync:person:user-name": True,
    # Allow name propagation with arbitrary user models...
    "sync:person:user-name:cn": "get_full_name",
    "sync:person:user-name:given_name": "first_name",
    "sync:person:user-name:sn": "last_name",
    # Sync model existence:
    #   *note* people are not deleted when users are deleted...
    "sync:person:user:create-delete": True,
    # ... unless this is set also
    #   (when this is False the person username is cleared upon User delete)
    "sync:person:user:create-delete:delete-person": False,
    # Sync email changes
    "sync:person:user-email": True,  #
    # Sync PersonFlags and auth.Groups; as well as the memberships.
    #   This is fairly aggressive, and syncs creates, updates, and deletes.
    "sync:person-flags:user-groups": True,
    # a callable or other way of slugify people (see django-autoslug docs)
    "person:slug:populate_from": "cn",
}

from django.conf import settings


def get(setting):
    """
    get(setting) -> value

    setting should be a string representing the application settings to
    retrieve.
    """
    assert setting in DEFAULT, "the setting %r has no default value" % setting
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return app_settings.get(setting, DEFAULT[setting])


def set(setting, value):
    """
    set(setting, value)

    Setting things programmatically should only ever happen in unit tests.
    """
    assert setting in DEFAULT, "the setting %r has no default value" % setting
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    app_settings[setting] = value
    return value


def get_all():
    """
    Return all current settings as a dictionary.
    """
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return dict(
        [(setting, app_settings.get(setting, DEFAULT[setting])) for setting in DEFAULT]
    )
