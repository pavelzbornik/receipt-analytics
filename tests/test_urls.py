# -*- coding: utf-8 -*-
"""URLs unit tests."""
import pytest


@pytest.mark.usefixtures("testapp")
class TestURLs:
    """URL tests."""

    def test_home(self, testapp):
        """Tests if the home page loads."""

        rv = testapp.get("/")
        assert rv.status_code == 200

    def test_login(self, testapp):
        """Tests if the login page loads."""

        rv = testapp.get("/login/")
        assert rv.status_code == 200

    def test_register(self, testapp):
        """Tests if the register page loads."""

        rv = testapp.get("/register")
        assert rv.status_code == 200

    def test_reset_password(self, testapp):
        """Tests if the reset password page loads."""

        rv = testapp.get("/reset_password_request")
        assert rv.status_code == 200

    def test_reset_password_form(self, testapp):
        """Tests if the reset password form page loads."""

        rv = testapp.get("/reset_password/1234")
        assert rv.status_code == 302

    def test_logout(self, testapp):
        """Tests if the logout page loads when not logged in."""

        rv = testapp.get("/logout/", expect_errors=True)
        assert rv.status_code == 401

    def test_user_profile(self, testapp):
        """Tests if the user profile page loads when not logged in."""

        rv = testapp.get("/user/profile", expect_errors=True)
        assert rv.status_code == 401

    def test_edit_user_profile(self, testapp):
        """Tests if the edit user profile page loads when not logged in."""

        rv = testapp.get("/user/edit_profile", expect_errors=True)
        assert rv.status_code == 401
