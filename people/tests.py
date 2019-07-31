"""
Tests for the people application.
"""
#######################################################################

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.test import TestCase

from . import conf, handlers
from .models import EmailAddress, Person, PersonFlag

#######################################################################


class BasicPerson(TestCase):
    """
    Test basic operations on the person object.
    """

    def setUp(self):
        person = Person.objects.create(
            given_name="First", sn="Person", cn="First Person", username="user1"
        )
        self.person1_pk = person.pk

    def tearDown(self):
        Person.objects.all().delete()

    def test_person_email(self):
        """
        """
        person = Person.objects.get_by_username("user1")

        def check_email(emailaddress_qs, expected_values):
            for email, expected in zip(emailaddress_qs, expected_values):
                self.assertEqual(email.address, expected)

        person.add_email(
            "nobody1@example.com",
            conf.get("default_contact_info_type"),
            preferred=False,
        )
        check_email(person.emailaddress_set.all(), ["nobody1@example.com"])

        person.add_email(
            "nobody2@example.com", conf.get("default_contact_info_type"), preferred=True
        )
        check_email(
            person.emailaddress_set.all(),
            ["nobody2@example.com", "nobody1@example.com"],
        )

        person.add_email(
            "nobody3@example.com",
            conf.get("default_contact_info_type"),
            preferred=False,
        )
        check_email(
            person.emailaddress_set.all(),
            ["nobody2@example.com", "nobody1@example.com", "nobody3@example.com"],
        )

        person.add_email(
            "nobody4@example.com", conf.get("default_contact_info_type"), public=True
        )
        check_email(
            person.emailaddress_set.all(),
            [
                "nobody4@example.com",
                "nobody2@example.com",
                "nobody1@example.com",
                "nobody3@example.com",
            ],
        )


#######################################################################


class SyncSignals(TestCase):
    """
    Test all configured sync signals.
    """

    def setUp(self):
        """
        Ensure all handlers are registered -- test everything.
        """
        self.unregister_signal_handlers()

        # Setup some test data
        UserModel = get_user_model()
        UserModel.objects.create(username="user1", first_name="First", last_name="User")
        UserModel.objects.create(username="userN", first_name="Nth", last_name="User")
        person = Person.objects.create(
            given_name="First", sn="Person", cn="First Person", username="user1"
        )
        self.person1_pk = person.pk
        person = Person.objects.create(
            given_name="Second", sn="Person", cn="Second Person", username="person2"
        )
        self.person2_pk = person.pk
        person = Person.objects.create(
            given_name="Third", sn="Person", cn="Third Person", username=None
        )
        self.person3_pk = person.pk

        flag = PersonFlag.objects.create(verbose_name="Test Group", slug="test-group")
        self.flag_pk = flag.pk
        group = Group.objects.create(name="Test Group")
        self.group_pk = group.pk

        flag = PersonFlag.objects.create(
            verbose_name="Existing Flag", slug="existing-flag"
        )
        group = Group.objects.create(name="Existing Group")

        # Register signal handlers even when not configured...
        if True:  # not conf.get('sync:person:user-name'):
            models.signals.post_save.connect(
                handlers.person_post_save_name_to_user, sender=Person
            )
            models.signals.post_save.connect(
                handlers.user_post_save_name_to_person, sender=UserModel
            )

        if True:  # not conf.get('sync:person:user:create-delete'):
            models.signals.post_save.connect(
                handlers.person_post_save_create_user, sender=Person
            )
            models.signals.post_delete.connect(
                handlers.person_post_delete_user_delete, sender=Person
            )
            models.signals.post_save.connect(
                handlers.user_post_save_create_person, sender=UserModel
            )
            models.signals.post_delete.connect(
                handlers.user_post_delete_person_delete, sender=UserModel
            )

        if True:  # not conf.get('sync:person:user-email'):
            models.signals.post_save.connect(
                handlers.user_post_save_email_to_person, sender=UserModel
            )
            models.signals.post_save.connect(
                handlers.emailaddress_post_save_email_to_user, sender=EmailAddress
            )

        if True:  # not conf.get('sync:person-flags:user-groups'):
            models.signals.pre_save.connect(
                handlers.personflag_pre_save_to_group, sender=PersonFlag
            )
            models.signals.post_delete.connect(
                handlers.personflag_post_delete_group_delete, sender=PersonFlag
            )
            models.signals.pre_save.connect(
                handlers.group_pre_save_to_personflag, sender=Group
            )
            models.signals.post_delete.connect(
                handlers.group_post_delete_personflag_delete, sender=Group
            )
            models.signals.m2m_changed.connect(
                handlers.person_flags_m2m_changed_handler, sender=Person.flags.through
            )
            models.signals.m2m_changed.connect(
                handlers.user_groups_m2m_changed_handler,
                sender=UserModel.groups.through,
            )

    def tearDown(self):
        """
        Cleanup
        """
        self.unregister_signal_handlers()

    def unregister_signal_handlers(self):
        """
        Unregister all signal handlers so they can be run in tests.
        """
        UserModel = get_user_model()
        models.signals.post_save.disconnect(
            handlers.person_post_save_name_to_user, sender=Person
        )
        models.signals.post_save.disconnect(
            handlers.user_post_save_name_to_person, sender=UserModel
        )

        models.signals.post_save.disconnect(
            handlers.person_post_save_create_user, sender=Person
        )
        models.signals.post_delete.disconnect(
            handlers.person_post_delete_user_delete, sender=Person
        )
        models.signals.post_save.disconnect(
            handlers.user_post_save_create_person, sender=UserModel
        )
        models.signals.post_delete.disconnect(
            handlers.user_post_delete_person_delete, sender=UserModel
        )

        models.signals.post_save.disconnect(
            handlers.user_post_save_email_to_person, sender=UserModel
        )
        models.signals.post_save.disconnect(
            handlers.emailaddress_post_save_email_to_user, sender=EmailAddress
        )

        models.signals.pre_save.disconnect(
            handlers.personflag_pre_save_to_group, sender=PersonFlag
        )
        models.signals.post_delete.disconnect(
            handlers.personflag_post_delete_group_delete, sender=PersonFlag
        )
        models.signals.pre_save.disconnect(
            handlers.group_pre_save_to_personflag, sender=Group
        )
        models.signals.post_delete.disconnect(
            handlers.group_post_delete_personflag_delete, sender=Group
        )
        models.signals.m2m_changed.disconnect(
            handlers.person_flags_m2m_changed_handler, sender=Person.flags.through
        )
        models.signals.m2m_changed.disconnect(
            handlers.user_groups_m2m_changed_handler, sender=UserModel.groups.through
        )

    def test_person_name_to_user_name_1(self):
        """
        When the person and user already exist.
        """
        person = Person.objects.get_by_username("user1")
        person.given_name = "John"
        person.sn = "Doe"
        person.cn = person.given_name + " " + person.sn
        person.save()

        UserModel = get_user_model()
        user = UserModel.objects.get(username="user1")
        self.assertEqual(person.given_name, user.first_name)
        self.assertEqual(person.sn, user.last_name)
        self.assertEqual(person.cn, user.get_full_name())

    def test_person_name_to_user_name_2(self):
        """
        When the person exists (but has a username) and user does not.
        """
        person = Person.objects.get_by_username("person2")
        person.given_name = "John"
        person.sn = "Doe"
        person.cn = person.given_name + " " + person.sn
        person.save()
        # should complete without exception

    def test_person_name_to_user_name_3(self):
        """
        When the person exists (but has no username) and user does not.
        """
        person = Person.objects.get(pk=self.person3_pk)
        person.given_name = "John"
        person.sn = "Doe"
        person.cn = person.given_name + " " + person.sn
        person.save()
        # should complete without exception

    def test_person_email_to_user_1(self):
        """
        When the person and user both exist, and the email is preferred.
        """
        person = Person.objects.get_by_username("user1")
        person.add_email(
            "nobody@example.com", conf.get("default_contact_info_type"), preferred=True
        )

        UserModel = get_user_model()
        user = UserModel.objects.get(username="user1")

        self.assertEqual(user.email, "nobody@example.com")

    def test_person_email_to_user_2(self):
        """
        When the person and user both exist, and the email is *not* preferred.
        """
        person = Person.objects.get_by_username("user1")
        person.add_email(
            "nobody1@example.com",
            conf.get("default_contact_info_type"),
            preferred=False,
        )
        person.add_email(
            "nobody2@example.com", conf.get("default_contact_info_type"), preferred=True
        )
        person.add_email(
            "nobody3@example.com",
            conf.get("default_contact_info_type"),
            preferred=False,
        )

        UserModel = get_user_model()
        user = UserModel.objects.get(username="user1")

        # The preferred email should always be propagated to the user...
        self.assertEqual(user.email, "nobody2@example.com")

    def test_person_email_to_user_3(self):
        """
        When the person exists but the user does not.
        """
        person = Person.objects.get_by_username("person2")
        person.add_email("nobody@example.com", conf.get("default_contact_info_type"))
        # should complete without exception

    def test_person_email_to_user_4(self):
        """
        When the person exists but the user does not.
        """
        person = Person.objects.get(pk=self.person3_pk)
        person.add_email("nobody@example.com", conf.get("default_contact_info_type"))
        # should complete without exception

    def test_create_person_creates_user_1(self):
        """
        Create a person with a username -> user gets created.
        """
        person = Person.objects.create(
            given_name="Fourth", sn="Person", cn="Fourth Person", username="person4"
        )
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username="person4")
        except UserModel.DoesNotExist:
            self.fail("User for person not created")

    def test_create_person_creates_user_2(self):
        """
        Create a person with a username -> user gets created.
        """
        person = Person.objects.create(
            given_name="Fourth",
            sn="Person",
            cn="Fourth Person",
            username="person4@example.com",
        )
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username="person4@example.com")
        except UserModel.DoesNotExist:
            self.fail("User for person not created")

    def test_add_username_to_person_creates_user_1(self):
        """
        Giving a username to an existing person creates the user, if it
        does not exist.
        """
        person = Person.objects.get(pk=self.person3_pk)
        person.username = "person3"
        person.save()

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username="person3")
        except UserModel.DoesNotExist:
            self.fail("User for person not created")

    def test_create_person_without_username(self):
        """
        Create a person with no username -> Nothing happens
        """
        person = Person.objects.create(
            given_name="Fourth", sn="Person", cn="Fourth Person", username=None
        )
        # Completes without exception.

    def test_person_delete_to_user_1(self):
        """
        Delete a person with corresponding user -> user is deleted
        """
        person = Person.objects.get_by_username("user1")
        person.delete()
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username="user1")
        except UserModel.DoesNotExist:
            pass
        else:
            self.fail("User still exists")

    def test_person_delete_to_user_2(self):
        """
        Delete a person with no corresponding user 
        """
        person = Person.objects.get_by_username("person2")
        person.delete()
        # Completes without exception

    def test_user_name_to_person_name_1(self):
        """
        Changes to a users name -> person name changes
        """
        UserModel = get_user_model()
        user = UserModel.objects.get(username="user1")
        user.first_name = "John"
        user.last_name = "Doe"
        user.save()

        person = Person.objects.get(username="user1")

        self.assertEqual(person.given_name, user.first_name)
        self.assertEqual(person.sn, user.last_name)
        self.assertEqual(person.cn, user.get_full_name())

    def test_user_name_to_person_name_2(self):
        """
        Changes to a users name (w/o) person does not throw exception
        """
        UserModel = get_user_model()
        user = UserModel.objects.get(username="userN")
        user.first_name = "John"
        user.last_name = "Doe"
        user.save()
        # Completes

    def test_user_email_to_person_basic(self):
        """
        user.email -> person preferred email.
        """
        value = "nobody-uetp-t1@example.com"
        UserModel = get_user_model()
        user = UserModel.objects.get(username="user1")
        user.email = value
        user.save()

        person = Person.objects.get(username="user1")

        self.assertEqual(person.emailaddress_set.get().address, value)

    def test_user_email_to_person_multpile(self):
        """
        user.email -> person preferred email.
        """
        UserModel = get_user_model()
        user = UserModel.objects.get(username="user1")
        person = Person.objects.get(username="user1")

        value = "nobody-uetp-t1@example.com"
        user.email = value
        user.save()
        self.assertEqual(person.emailaddress_set.active()[0].address, value)

        # now add another email address so that we get check the person
        #   gets updated properly.
        value = "nobody-uetp-t2@example.com"
        user.email = value
        user.save()
        self.assertEqual(person.emailaddress_set.active()[0].address, value)

    def test_user_email_without_person(self):
        """
        user.email with no person model does nothing bad.
        """
        UserModel = get_user_model()
        user = UserModel.objects.get(username="userN")
        user.email = "nobody-uetp-t3@example.com"
        user.save()
        # completes w/o exception

    def test_user_create_to_person_1(self):
        """
        Create a new user -> person gets created.
        """
        UserModel = get_user_model()
        user = UserModel.objects.create(
            username="userM",
            first_name="Mth",
            last_name="User",
            email="user-m@example.com",
        )
        person = Person.objects.get_by_user(user)
        # completes w/o exception.

    def test_user_delete_to_person_clear_username_1(self):
        """
        Delete a user -> person username gets cleared.
        """
        conf.set("sync:person:user:create-delete:delete-person", False)
        UserModel = get_user_model()
        user = UserModel.objects.get(username="user1")
        user.delete()

        try:
            person = Person.objects.get(pk=self.person1_pk)
        except Person.DoesNotExist:
            self.fail("Person deleted")
        else:
            self.assertIsNone(person.username)

    def test_user_delete_to_person_clear_username_2(self):
        """
        Delete a user w/o person succeeds
        """
        conf.set("sync:person:user:create-delete:delete-person", False)
        UserModel = get_user_model()
        user = UserModel.objects.get(username="userN")
        user.delete()
        # no problem

    def test_user_delete_to_person_full_delete_1(self):
        """
        Delete a user -> person gets deleted
        """
        conf.set("sync:person:user:create-delete:delete-person", True)
        UserModel = get_user_model()
        user = UserModel.objects.get(username="user1")
        user.delete()

        try:
            person = Person.objects.get(username="user1")
        except Person.DoesNotExist:
            pass
        else:
            self.fail("Person still exists")

    def test_user_delete_to_person_full_delete_2(self):
        """
        Delete a user -> person gets deleted
        """
        conf.set("sync:person:user:create-delete:delete-person", True)
        UserModel = get_user_model()
        user = UserModel.objects.get(username="userN")
        user.delete()
        # passes w/o exception

    def test_personflag_create_to_group_1(self):
        """
        Create a person flag -> group gets created
        """
        flag = PersonFlag.objects.create(verbose_name="New Group", slug="new-group")
        try:
            group = Group.objects.get(name="New Group")
        except Group.DoesNotExist:
            self.fail("Group was not created")

    def test_personflag_create_to_group_2(self):
        """
        Create a person flag -> Does not blow up when group exists already.
        """
        flag = PersonFlag.objects.create(
            verbose_name="Existing Group", slug="existing-group"
        )
        try:
            group = Group.objects.get(name="Existing Group")
        except Group.DoesNotExist:
            self.fail("Group was not created")

    def test_personflag_rename_to_group_1(self):
        """
        Rename a person flag -> group gets renamed
        """
        flag = PersonFlag.objects.get(pk=self.flag_pk)
        flag.verbose_name = "Renamed Group"
        flag.save()
        try:
            group = Group.objects.get(name="Renamed Group")
        except Group.DoesNotExist:
            self.fail("Group does not exist")
        else:
            self.assertEqual(group.pk, self.group_pk)

    def test_personflag_rename_to_group_2(self):
        """
        Rename a person flag to pre-existing group 
        -- not defined, but not ill-behaved.
        """
        flag = PersonFlag.objects.get(pk=self.flag_pk)
        flag.verbose_name = "Existing Group"
        flag.save()
        try:
            group = Group.objects.get(name="Existing Group")
        except Group.DoesNotExist:
            self.fail("Group does not exist")

    def test_personflag_rename_no_existing_group(self):
        """
        Rename a person flag to when there is no pre-existing group 
        -- creates a new group
        """
        flag = PersonFlag.objects.get(verbose_name="Existing Flag")
        flag.verbose_name = "New Flag Group"
        flag.save()
        try:
            group = Group.objects.get(name="New Flag Group")
        except Group.DoesNotExist:
            self.fail("Group does not exist")

    def test_personflag_delete_to_group_1(self):
        """
        Delete person flag -> group is deleted.
        """
        flag = PersonFlag.objects.get(pk=self.flag_pk)
        flag.delete()
        try:
            group = Group.objects.get(name="Test Group")
        except Group.DoesNotExist:
            pass
        else:
            self.fail("Group should not exist")

    def test_personflag_delete_to_group_2(self):
        """
        Delete person flag well behaved when group does not exist.
        """
        flag = PersonFlag.objects.get(verbose_name="Existing Flag")
        flag.delete()
        # no whammies.

    def test_group_create_to_personflag_1(self):
        """
        Create a group -> person flag gets created.
        """
        group = Group.objects.create(name="New Group")
        try:
            flag = PersonFlag.objects.get(verbose_name="New Group")
        except PersonFlag.DoesNotExist:
            self.fail("PersonFlag not created")

    def test_group_create_to_personflag_2(self):
        """
        Create a group well behaved when flag already exists
        """
        group = Group.objects.create(name="Existing Flag")
        try:
            flag = PersonFlag.objects.get(verbose_name="Existing Flag")
        except PersonFlag.DoesNotExist:
            self.fail("PersonFlag not created")

    def test_group_rename_to_personflag_1(self):
        """
        Rename a group -> corresponding person flag renamed.
        """
        group = Group.objects.get(pk=self.group_pk)
        group.name = "Renamed Group"
        group.save()
        try:
            flag = PersonFlag.objects.get(verbose_name="Renamed Group")
        except PersonFlag.DoesNotExist:
            self.fail("PersonFlag not renamed")
        else:
            self.assertEqual(flag.pk, self.flag_pk)

    def test_group_rename_to_personflag_already_exists(self):
        """
        Rename a group to a name that already has a flag.
        """
        group = Group.objects.get(name="Existing Group")
        group.name = "Existing Flag"
        group.save()
        try:
            flag = PersonFlag.objects.get(verbose_name="Existing Flag")
        except PersonFlag.DoesNotExist:
            self.fail("PersonFlag not found")

    def test_group_rename_to_personflag_3(self):
        """
        Rename a group to a name that has no pre-existing flag.
        """
        group = Group.objects.get(name="Existing Group")
        group.name = "New Flag Group"
        group.save()
        try:
            flag = PersonFlag.objects.get(verbose_name="New Flag Group")
        except PersonFlag.DoesNotExist:
            self.fail("PersonFlag not found or created")

    def test_group_delete_to_personflag_1(self):
        """
        Delete a group -> person flag also deleted.
        """
        group = Group.objects.get(pk=self.group_pk)
        group.delete()
        try:
            flag = PersonFlag.objects.get(verbose_name="Test Group")
        except PersonFlag.DoesNotExist:
            pass
        else:
            self.fail("PersonFlag should have been deleted")

    def test_group_delete_to_personflag_2(self):
        """
        Delete a group w/o person flag is well behaved
        """
        group = Group.objects.get(name="Existing Group")
        group.delete()
        # no exceptions.

    def test_person_flag_membership_to_user_group(self):
        """
        Changing the flags of a person ==> Change of groups for user.
        """
        person = Person.objects.get(username="user1")
        personflag = PersonFlag.objects.get(verbose_name="Test Group")

        person.flags.add(personflag)

        UserModel = get_user_model()
        user = UserModel.objects.get(username="user1")
        group = Group.objects.get(name="Test Group")
        self.assertIn(group, user.groups.all())

        second_flag = PersonFlag.objects.get(verbose_name="Existing Flag")
        person.flags.add(second_flag)
        second_group = Group.objects.get(name="Existing Flag")
        self.assertIn(second_group, user.groups.all())

        person.flags.remove(personflag)
        self.assertNotIn(group, user.groups.all())
        self.assertIn(second_group, user.groups.all())

        person.flags.clear()
        self.assertFalse(user.groups.exists())

    def test_user_group_membership_to_person_flag(self):
        """
        Change of groups for user ==> Changing the flags of a person
        """
        UserModel = get_user_model()
        user = UserModel.objects.get(username="user1")

        group = Group.objects.get(name="Test Group")
        user.groups.add(group)

        person = Person.objects.get(username="user1")
        personflag = PersonFlag.objects.get(verbose_name="Test Group")

        self.assertIn(personflag, person.flags.all())

        second_group = Group.objects.get(name="Existing Group")
        user.groups.add(second_group)
        second_flag = PersonFlag.objects.get(verbose_name="Existing Group")
        self.assertIn(second_flag, person.flags.all())

        user.groups.remove(group)
        self.assertNotIn(personflag, person.flags.all())
        self.assertIn(second_flag, person.flags.all())

        user.groups.clear()
        self.assertFalse(person.flags.exists())


#######################################################################
