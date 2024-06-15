# -*- coding: utf-8 -*-
"""Test forms."""

from flask_login import login_user

from app.user.forms import (
    EditProfileForm,
    LoginForm,
    RegisterForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)


class TestRegisterForm:
    """Register form."""

    def test_validate_user_already_registered(self, user):
        """Enter username that is already registered."""
        form = RegisterForm(
            username=user.username,
            email="foo@bar.com",
            password="example",
            confirm="example",
        )

        assert form.validate() is False
        assert "Username already registered" in form.username.errors

    def test_validate_email_already_registered(self, user):
        """Enter email that is already registered."""
        form = RegisterForm(
            username="unique",
            email=user.email,
            password="example",
            confirm="example",
        )

        assert form.validate() is False
        assert "Email already registered" in form.email.errors

    def test_validate_success(self, db):
        """Register with success."""
        form = RegisterForm(
            username="newusername",
            email="new@test.com",
            password="example",
            confirm="example",
        )
        assert form.validate() is True


class TestLoginForm:
    """Login form."""

    def test_validate_success(self, user):
        """Login successful."""
        user.save()
        form = LoginForm(username=user.username, password="myprecious")
        assert form.validate() is True
        assert form.user == user

    def test_validate_unknown_username(self, db):
        """Unknown username."""
        form = LoginForm(username="unknown", password="example")
        assert form.validate() is False
        assert "Unknown username" in form.username.errors
        assert form.user is None

    def test_validate_invalid_password(self, user):
        """Invalid password."""
        user.save()
        form = LoginForm(username=user.username, password="wrongpassword")
        assert form.validate() is False
        assert "Invalid password" in form.password.errors

    def test_validate_inactive_user(self, user):
        """Inactive user."""
        user.active = False
        user.save()
        # Correct username and password, but user is not activated
        form = LoginForm(username=user.username, password="myprecious")
        assert form.validate() is False
        assert "User not activated" in form.username.errors


class TestEditProfileForm:
    """Edit profile form tests."""

    def test_validate_success(self, app, user):
        """Test form validates with valid data."""
        with app.test_request_context():
            login_user(user)
            form = EditProfileForm(
                username="validuser",
                email="validemail@example.com",
                first_name="John",
                last_name="Doe",
            )
            assert form.validate() is True

    def test_validate_missing_username(self, app):
        """Test form fails without a username."""
        form = EditProfileForm(
            username="",
            email="validemail@example.com",
            first_name="John",
            last_name="Doe",
        )
        assert form.validate() is False
        assert "This field is required." in form.username.errors

    def test_validate_short_username(self, app):
        """Test form fails with a too short username."""
        form = EditProfileForm(
            username="ab",
            email="validemail@example.com",
            first_name="John",
            last_name="Doe",
        )
        assert form.validate() is False
        assert "Field must be between 3 and 25 characters long." in form.username.errors

    def test_validate_long_username(self, app):
        """Test form fails with a too long username."""
        form = EditProfileForm(
            username="a" * 26,
            email="validemail@example.com",
            first_name="John",
            last_name="Doe",
        )
        assert form.validate() is False
        assert "Field must be between 3 and 25 characters long." in form.username.errors

    def test_validate_invalid_email(self, app):
        """Test form fails with an invalid email."""
        form = EditProfileForm(
            username="validuser",
            email="invalidemail",
            first_name="John",
            last_name="Doe",
        )
        assert form.validate() is False
        assert "Invalid email address." in form.email.errors

    def test_validate_missing_first_name(self, app):
        """Test form fails without a first name."""
        form = EditProfileForm(
            username="validuser",
            email="validemail@example.com",
            first_name="",
            last_name="Doe",
        )
        assert form.validate() is False
        assert "This field is required." in form.first_name.errors

    def test_validate_missing_last_name(self, app):
        """Test form fails without a last name."""
        form = EditProfileForm(
            username="validuser",
            email="validemail@example.com",
            first_name="John",
            last_name="",
        )
        assert form.validate() is False
        assert "This field is required." in form.last_name.errors


class TestResetPasswordRequestForm:
    """Tests for ResetPasswordRequestForm."""

    def test_validate_success(self, user):
        """Test form validation on successful submission."""

        form = ResetPasswordRequestForm(email=user.email)
        assert form.validate() is True

    def test_validate_invalid_email(self, app):
        """Test form validation with invalid email."""

        form = ResetPasswordRequestForm(email="invalid-email")

        assert form.validate() is False
        assert "Invalid email address." in form.email.errors


class TestResetPasswordForm:
    """Tests for ResetPasswordForm."""

    def test_validate_success(self, app):
        """Test form validation on successful submission."""
        form = ResetPasswordForm(password="newpassword", confirm="newpassword")

        assert form.validate() is True

    def test_validate_passwords_not_matching(self, app):
        """Test form validation when passwords do not match."""
        form = ResetPasswordForm(password="newpassword", confirm="mismatched")

        assert form.validate() is False
        assert "Passwords must match" in form.confirm.errors

    def test_validate_short_password(self, app):
        """Test form validation with a too short password."""
        form = ResetPasswordForm(password="short", confirm="short")

        assert form.validate() is False
        assert "Field must be between 6 and 40 characters long." in form.password.errors

    def test_validate_long_password(self, app):
        """Test form validation with a too long password."""
        form = ResetPasswordForm(password="a" * 41, confirm="a" * 41)

        assert form.validate() is False
        assert "Field must be between 6 and 40 characters long." in form.password.errors
