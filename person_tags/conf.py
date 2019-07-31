"""
The DEFAULT configuration is loaded when the CONFIG_NAME dictionary
is not present in your settings.

All valid application settings must have a default value.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.core.files.storage import default_storage

CONFIG_NAME = "PERSON_TAGS_CONFIG"  # must be uppercase!

#############################################################

DEFAULT = {
    # 'storage' is the storage backend for files.
    # (optional)
    "storage": default_storage,
    # 'upload_to' is the variable portion of the path where files are stored.
    # (optional)
    "upload_to": "person-tags/%Y/%m",
}

#############################################################


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
