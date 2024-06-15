# -*- coding: utf-8 -*-
"""User models."""
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Column, TableModel, db, reference_col, relationship
from app.extensions import bcrypt


class Role(TableModel):
    """A role for a user."""

    __tablename__ = "roles"
    name: Mapped[str] = Column(db.String(80), unique=True, nullable=False)
    user_id: Mapped[int] = reference_col("users", nullable=True)
    user = relationship("User", backref="roles")

    def __init__(self, name, **kwargs):
        """Create instance."""
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Role({self.name})>"


class User(UserMixin, TableModel):
    """A user of the app."""

    __tablename__ = "users"
    username: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)
    _password = mapped_column("password", db.LargeBinary(128), nullable=True)
    first_name: Mapped[str] = mapped_column(db.String(30), nullable=True)
    last_name: Mapped[str] = mapped_column(db.String(30), nullable=True)
    active: Mapped[bool] = mapped_column(db.Boolean(), default=False)
    is_admin: Mapped[bool] = mapped_column(db.Boolean(), default=False)

    @hybrid_property
    def password(self):
        """Hashed password."""
        return self._password

    @password.setter
    def password(self, value):
        """Set password."""
        self._password = bcrypt.generate_password_hash(value)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self._password, value)

    def get_user_by_email(self, email):
        """Get user by email."""
        return User.query.filter_by(email=email).first()

    def get_reset_password_token(self, expires_in=600):
        """Get reset password token."""
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        """Verify reset password token."""
        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            user_id = payload["reset_password"]
            return User.get_by_id(user_id)
        except ExpiredSignatureError:
            current_app.logger.error("Token has expired")
            return None
        except InvalidTokenError:
            current_app.logger.error("Invalid token")
            return None
        except KeyError:
            current_app.logger.error("'reset_password' key missing in token")
            return None

    @property
    def full_name(self):
        """Full user name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<User({self.username!r})>"
