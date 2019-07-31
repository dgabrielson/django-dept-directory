import sys
from datetime import timedelta
from io import StringIO

from django.conf import settings
from django.core.mail import mail_admins

from celery.task import PeriodicTask

from .cli.verify_email_cleanup import main as verify_email_cleanup

###############################################################


class VerifyEmailCleanup(PeriodicTask):
    run_every = timedelta(hours=24)

    def run(self, **kwargs):

        output = StringIO()

        _stdout = sys.stdout
        _stderr = sys.stderr

        sys.stdout = output
        sys.stderr = output

        verify_email_cleanup({}, [])

        sys.stdout = _stdout
        sys.stderr = _stderr

        results = output.getvalue().strip()
        if results:
            if getattr(settings, "ADMINS", ()):
                mail_admins(self.name, results)
            else:
                logger = self.get_logger(**kwargs)
                logger.error("Message for ADMINS, but no ADMINS set")


###############################################################
