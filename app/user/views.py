# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.utils import flash_errors

from .forms import EditProfileForm
from .models import User

blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")


@blueprint.route("/")
@login_required
def members():
    """List members."""
    return render_template("users/members.html")


@blueprint.route("/profile")
@login_required
def user():
    user = User.get_by_id(current_user.id)
    return render_template("users/user.html", user=user)


@blueprint.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
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
    return render_template("users/edit_profile.html", title="Edit Profile", form=form)
