"""
The DEFAULT configuration is loaded when the named _CONFIG dictionary
is not present in your settings.
"""

CONFIG_NAME = "DIRECTORY_CONFIG"  # must be uppercase!

# NOTE: we use django-phonenumber-field for phone numbers;
#   with a behaviour of NATIONAL format with INTERNATIONAL fallback.
# In your global projects settings; you should set:
# PHONENUMBER_DEFAULT_REGION = 'US'
# with your region as appropriate.  See phonenumbers/data/region_*.py
# for the supported list (ISO alpha-2)

DEFAULT = {
    "localflavor": {
        "region": "django_localflavor_us.forms.USStateField",
        "postalcode": "django_localflavor_us.forms.USZipCodeField",
    },
    "office_model": "places.Office",
    # This folder exists in MEDIA_ROOT, must be writable by the admin:
    #   sudo chown -R :www-data faces
    #   chmod -R g+rwx faces
    "mugshot_path": "directory/faces/%Y/%m",
    "print_context": {
        # remember to use double-backslash for LaTeX commands.
        "geometry": "",
        "at_document_start": "",
    },
    # This is used by the update_sessionals CLI management command.
    #   If you're not using this, you can ignore this setting.
    "update_sessionals": {
        "section:type:exclude": ["00", "lb", "zz"],
        "academic:type:slug_list": ["academic-staff", "co-op-coordinator"],
        "sessional:type:slug_list": [
            "sessional-instructors",
            "full-time-sessional-instructors",
        ],
        "cn:blacklist": [],
    },
    # specify the domain '@example.com' for aggregate mailing lists.
    # using None disables the generation of aggregate directory lists.
    "mailing-lists:domain": None,
    # for each entrytype slug listed: signals automatically handle personflags
    # which correspond to entrytypes.  The slug '__all__' indicates what
    # you would expect.
    "signals:entrytypes-personflags": [],
    # This next setting allows all directory entry types to be personflags
    #   but not all personflags become directory entry types, unless ``True``.
    "signals:entrytypes-personflags:personflag-fwd-on": False,
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


def get_all():
    """
    Return all current settings as a dictionary.
    """
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return dict(
        [(setting, app_settings.get(setting, DEFAULT[setting])) for setting in DEFAULT]
    )
