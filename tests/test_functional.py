# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from flask import url_for

from app.extensions import mail
from app.user.models import User

from .factories import UserFactory


class TestLoggingIn:
    """Login."""

    def test_can_log_in_returns_200(self, user, testapp):
        """Login successful."""
        # Goes to login page
        res = testapp.get(url_for("user.login"))
        # Fills out login form in navbar
        form = res.forms["loginForm"]
        form["username"] = user.username
        form["password"] = "myprecious"
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200

    def test_sees_alert_on_log_out(self, user, testapp):
        """Show alert on logout."""
        res = testapp.get(url_for("user.login"))
        # Fills out login form in navbar
        form = res.forms["loginForm"]
        form["username"] = user.username
        form["password"] = "myprecious"
        # Submits
        res = form.submit().follow()
        res = testapp.get(url_for("user.logout")).follow()
        # sees alert
        assert "You are logged out." in res

    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        """Show error if password is incorrect."""
        # Goes to homepage
        res = testapp.get(url_for("user.login"))
        # Fills out login form, password incorrect
        form = res.forms["loginForm"]
        form["username"] = user.username
        form["password"] = "wrong"
        # Submits
        res = form.submit()
        # sees error
        assert "Invalid password" in res

    def test_sees_error_message_if_username_doesnt_exist(self, user, testapp):
        """Show error if username doesn't exist."""
        # Goes to homepage
        res = testapp.get(url_for("user.login"))
        # Fills out login form, password incorrect
        form = res.forms["loginForm"]
        form["username"] = "unknown"
        form["password"] = "myprecious"
        # Submits
        res = form.submit()
        # sees error
        assert "Unknown user" in res


class TestRegistering:
    """Register a user."""

    def test_can_register(self, user, testapp):
        """Register a new user."""
        old_count = len(User.query.all())
        # Goes to homepage
        res = testapp.get(url_for("user.register"))
        # Clicks Create Account button
        # res = res.click("Create account")
        # Fills out the form
        form = res.forms["registerForm"]
        form["username"] = "foobar"
        form["email"] = "foo@bar.com"
        form["password"] = "secret"
        form["confirm"] = "secret"
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200
        # A new user was created
        assert len(User.query.all()) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        """Show error if passwords don't match."""
        # Goes to registration page
        res = testapp.get(url_for("user.register"))
        # Fills out form, but passwords don't match
        form = res.forms["registerForm"]
        form["username"] = "foobar"
        form["email"] = "foo@bar.com"
        form["password"] = "secret"
        form["confirm"] = "secrets"
        # Submits
        res = form.submit()
        # sees error message
        assert "Passwords must match" in res

    def test_sees_error_message_if_user_already_registered(self, user, testapp):
        """Show error if user already registered."""
        user = UserFactory(active=True)  # A registered user
        user.save()
        # Goes to registration page
        res = testapp.get(url_for("user.register"))
        # Fills out form, but username is already registered
        form = res.forms["registerForm"]
        form["username"] = user.username
        form["email"] = "foo@bar.com"
        form["password"] = "secret"
        form["confirm"] = "secret"
        # Submits
        res = form.submit()
        # sees error
        assert "Username already registered" in res


class TestEditProfile:
    """Edit profile."""

    def test_can_edit_profile(self, user, testapp, db):
        """Edit an existing user's profile."""
        # Logs in the user
        res = testapp.get(url_for("user.login"))
        form = res.forms["loginForm"]
        form["username"] = user.username
        form["password"] = "myprecious"  # Assuming you know the test user's password
        res = form.submit().follow()

        # Goes to edit profile page
        res = testapp.get(url_for("user.edit_profile"))
        # Fills out the form
        form = res.forms["editProfileForm"]
        form["username"] = "newusername"
        form["email"] = "newemail@example.com"
        form["first_name"] = "NewFirstName"
        form["last_name"] = "NewLastName"
        # Submits
        res = form.submit()
        assert res.status_code == 302
        res = res.follow()

        # The user's profile was updated
        test_user = db.session.get(User, user.id)
        assert test_user.username == "newusername"
        assert test_user.email == "newemail@example.com"
        assert test_user.first_name == "NewFirstName"
        assert test_user.last_name == "NewLastName"

    def test_sees_error_message_if_username_already_exists(self, user, testapp, db):
        """Show error if username is already registered."""
        # Create another user with a different username
        another_user = User(
            username="existingusername",
            email="existing@example.com",
            password="password",
        )
        db.session.add(another_user)
        db.session.commit()

        # Logs in the user
        res = testapp.get(url_for("user.login"))
        form = res.forms["loginForm"]
        form["username"] = user.username
        form["password"] = "myprecious"  # Assuming you know the test user's password
        res = form.submit().follow()

        # Goes to edit profile page
        res = testapp.get(url_for("user.edit_profile"))
        # Fills out the form with an existing username
        form = res.forms["editProfileForm"]
        form["username"] = "existingusername"
        form["email"] = "newemail@example.com"
        form["first_name"] = "NewFirstName"
        form["last_name"] = "NewLastName"
        # Submits
        res = form.submit()
        # sees error
        assert "Username already registered" in res

    def test_sees_error_message_if_email_already_exists(self, user, testapp, db):
        """Show error if email is already registered."""
        # Create another user with a different email
        another_user = User(
            username="newuser",
            email="existing@example.com",
            password="password",
        )
        db.session.add(another_user)
        db.session.commit()

        # Logs in the user
        res = testapp.get(url_for("user.login"))
        form = res.forms["loginForm"]
        form["username"] = user.username
        form["password"] = "myprecious"  # Assuming you know the test user's password
        res = form.submit().follow()

        # Goes to edit profile page
        res = testapp.get(url_for("user.edit_profile"))
        # Fills out the form with an existing email
        form = res.forms["editProfileForm"]
        form["username"] = "newusername"
        form["email"] = "existing@example.com"
        form["first_name"] = "NewFirstName"
        form["last_name"] = "NewLastName"
        # Submits
        res = form.submit()
        # sees error
        assert "Email already registered" in res

    def test_sees_error_message_if_required_fields_missing(self, user, testapp):
        """Show error if required fields are missing."""
        # Logs in the user
        res = testapp.get(url_for("user.login"))
        form = res.forms["loginForm"]
        form["username"] = user.username
        form["password"] = "myprecious"  # Assuming you know the test user's password
        res = form.submit().follow()

        # Goes to edit profile page
        res = testapp.get(url_for("user.edit_profile"))
        # Fills out the form with missing required fields
        form = res.forms["editProfileForm"]
        form["username"] = ""
        form["email"] = ""
        form["first_name"] = ""
        form["last_name"] = ""
        # Submits
        res = form.submit()
        # sees errors
        assert "This field is required." in res


class TestResetPassword:
    """Reset password request."""

    def test_can_request_password_reset(self, user, testapp):
        """Request a password reset."""
        # Visit the reset password request page
        res = testapp.get(url_for("user.reset_password_request"))
        # Fill out the form
        form = res.forms["resetPasswordRequestForm"]
        with mail.record_messages() as outbox:
            form["email"] = user.email
            # Submit the form
            res = form.submit().follow()

            print(outbox[0].body)
            # Check that the user is redirected to the login page
            assert res.status_code == 200
            assert url_for("user.login") in res.request.url
            assert len(outbox) == 1

    def test_request_password_reset_not_existing_email(self, testapp, db):
        """Request a password reset with an invalid email."""
        # Visit the reset password request page
        res = testapp.get(url_for("user.reset_password_request"))
        # Fill out the form with an not existing email
        form = res.forms["resetPasswordRequestForm"]
        with mail.record_messages() as outbox:
            form["email"] = "notexistingemail@example.com"
            # Submit the form
            res = form.submit()
            # Check that the user is redirected to the same page
            assert res.status_code == 302
            assert url_for("user.reset_password_request") in res.request.url
            assert len(outbox) == 0

    def test_password_reset_flow(self, testapp, user):
        """Test the password reset flow."""
        # 1. Request a password reset
        res = testapp.get(url_for("user.reset_password_request"))
        form = res.forms["resetPasswordRequestForm"]
        form["email"] = user.email
        with mail.record_messages() as outbox:
            res = form.submit().follow()
            assert res.status_code == 200
            assert url_for("user.login") in res.request.url
            assert len(outbox) == 1  # Ensure only one email was sent

            # 2. Extract the reset token from the email
            reset_email = outbox[0]

            # Extracting the token using a regex or any method suitable to your email format
            import re

            reset_link = re.search(r"https?://[^\s]+", reset_email.body).group(0)
            reset_token = reset_link.split("/")[-1]

            # 3. Reset the password using the token
            reset_url = url_for("user.reset_password", token=reset_token)
            res = testapp.get(reset_url)
            form = res.forms["resetPasswordForm"]
            form["password"] = "new_password"  # Set a new password here
            form["confirm"] = "new_password"
            res = form.submit().follow()
            assert res.status_code == 200
            assert "Your password has been reset." in res
