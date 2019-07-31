"""
Celery Tasks for the Aurora app.
"""
###############################################################

import sys
from datetime import timedelta
from io import StringIO

from django.conf import settings
from django.core.mail import mail_admins

from celery.schedules import crontab
from celery.task import PeriodicTask

from .cli.update_sessionals import main as update_sessionals

###############################################################


class CLITaskRunMixin(object):
    def cli_taskrun_wrapper(self, func, options, args):
        """
        A completely generic CLI run wrapper.
        """
        output = StringIO()

        _stdout = sys.stdout
        _stderr = sys.stderr

        sys.stdout = output
        sys.stderr = output

        value = func(options, args)

        sys.stdout = _stdout
        sys.stderr = _stderr

        results = output.getvalue().strip()
        if results:
            if getattr(settings, "ADMINS", ()):
                mail_admins(self.name, results)
            else:
                logger = self.get_logger(**kwargs)
                logger.error("Message for ADMINS, but no ADMINS set")

        return value


###############################################################


class UpdateSessionals(PeriodicTask, CLITaskRunMixin):
    run_every = timedelta(hours=24)

    def run(self, **kwargs):
        return self.cli_taskrun_wrapper(update_sessionals, {}, [])


###############################################################
