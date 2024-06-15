# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import login_manager
from app.user.email import send_password_reset_email
from app.utils import flash_errors

from .forms import (
    EditProfileForm,
    LoginForm,
    RegisterForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)
from .models import User

blueprint = Blueprint("user", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        flash("Thank you for registering. You can now log in.", "success")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template(
        "form.html",
        form=form,
        title="Register",
        form_id="registerForm",
        sub_text=f"""<p><em>Already registered?</em>
          Click <a href="{url_for('user.login')}">here</a> to login.</p>""",
    )


@blueprint.route("/login/", methods=["GET", "POST"])
def login():
    """Login."""
    if current_user.is_authenticated:
        return redirect(url_for("user.profile"))
    """Login page."""
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", "success")
            redirect_url = request.args.get("next") or url_for("user.profile")
            return redirect(redirect_url)
        else:
            flash_errors(form)

    return render_template(
        "form.html",
        form=form,
        form_id="loginForm",
        title="Login",
        sub_text=f"""<a href="{url_for('user.reset_password_request')}" class="btn btn-danger">Forgot password</a>
        <p><em>Don't have an account yet? </em>
        <a href="{url_for('user.register')}">Create account</a></p>""",
    )


@blueprint.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    """Reset password."""
    if current_user.is_authenticated:
        return redirect(url_for("user.profile"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User().get_user_by_email(email=form.email.data)
        if user:
            # pass
            send_password_reset_email(user)
        flash(
            "Check your email for the instructions to reset your password",
            "success",
        )
        return redirect(url_for("user.login"))
    return render_template(
        "form.html",
        form=form,
        form_id="resetPasswordRequestForm",
        title="Reset Password",
    )


@blueprint.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset the user's password."""
    if current_user.is_authenticated:
        return redirect(url_for("public.home"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("public.home"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        user.save()
        flash("Your password has been reset.", "success")
        return redirect(url_for("user.login"))
    return render_template(
        "form.html",
        form=form,
        form_id="resetPasswordForm",
        title="Reset Your Password",
    )


@blueprint.route("/profile/")
@login_required
def profile():
    """List members."""
    return render_template("users/profile.html")


@blueprint.route("/user/profile")
@login_required
def user():
    """List user detail."""
    user = User.get_by_id(current_user.id)
    return render_template("users/user.html", user=user)


@blueprint.route("/user/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Edit profile."""
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        User.update(current_user)
        flash("Your changes have been saved.")
        return redirect(url_for("user.user", id=current_user.id))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    else:
        flash_errors(form)
    return render_template(
        "form.html",
        title="Edit Profile",
        form=form,
        form_id="editProfileForm",
        nav_bar="users/partials/_settings_nav.html",
        active_tab="edit_profile",
    )
