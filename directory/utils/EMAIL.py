"""
Email synchronizer for the directory app.
"""

from .. import conf
from ..models import DirectoryEntry


def main():
    entries = DirectoryEntry.objects.active()

    mail_domain = conf.get("mailing-lists:domain")

    results = {}
    for e in entries:
        if e.person.email is None:
            continue
        if e.type.slug not in results:
            results[e.type.slug] = []
        results[e.type.slug].append(e.person.email.address)

    if mail_domain is not None:
        if not mail_domain.startswith("@"):
            mail_domain = "@" + mail_domain
        results["all-directory"] = [e + mail_domain for e in results.keys()]
        results["staff"] = [
            e + mail_domain
            for e in ["academic-staff", "sessional-instructors", "support-staff"]
        ]
        results["grad-students"] = [
            e + mail_domain for e in ["phd-students", "msc-students"]
        ]

    for key in results:
        values = results[key]
        results[key] = ",".join(values)
    return results
