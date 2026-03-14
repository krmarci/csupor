from __future__ import annotations

import enum
from datetime import date

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


class UserPrivilege(enum.Enum):
    employee = "employee"
    hr = "hr"
    ceo = "ceo"
    developer = "developer"


class Gender(enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    privilege = db.Column(db.Enum(UserPrivilege), nullable=False, default=UserPrivilege.employee)

    profile = db.relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    dependents = db.relationship("Dependent", back_populates="user", cascade="all, delete-orphan")
    qualifications = db.relationship(
        "EducationalQualification", back_populates="user", cascade="all, delete-orphan"
    )
    professional_exam = db.relationship(
        "ProfessionalExam", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    full_name = db.Column(db.String(120), nullable=True)
    name_at_birth = db.Column(db.String(120), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    place_of_birth = db.Column(db.String(120), nullable=True)
    gender = db.Column(db.Enum(Gender), nullable=True)
    mothers_maiden_name = db.Column(db.String(120), nullable=True)
    citizenships = db.Column(db.String(255), nullable=True)
    social_security_number = db.Column(db.String(9), nullable=True)
    tax_number = db.Column(db.String(10), nullable=True)
    education_number = db.Column(db.String(11), nullable=True)
    teacher_id_card_number = db.Column(db.String(64), nullable=True)
    permanent_residence = db.Column(db.String(255), nullable=True)
    temporary_address = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(40), nullable=True)
    bank_account_number = db.Column(db.String(64), nullable=True)
    marital_status = db.Column(db.String(64), nullable=True)
    disability = db.Column(db.String(255), nullable=True)

    user = db.relationship("User", back_populates="profile")


class Dependent(db.Model):
    __tablename__ = "dependents"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    social_security_number = db.Column(db.String(9), nullable=False)
    dependency_start = db.Column(db.Date, nullable=False)
    disability = db.Column(db.String(255), nullable=True)

    user = db.relationship("User", back_populates="dependents")


class EducationalQualification(db.Model):
    __tablename__ = "educational_qualifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    level_or_type = db.Column(db.String(120), nullable=False)
    qualification_name = db.Column(db.String(120), nullable=False)
    institution_name = db.Column(db.String(120), nullable=False)
    degree_number = db.Column(db.String(80), nullable=False)
    year_obtained = db.Column(db.Integer, nullable=False)
    highest = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship("User", back_populates="qualifications")


class ProfessionalExam(db.Model):
    __tablename__ = "professional_exams"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    qualification_name = db.Column(db.String(120), nullable=False)
    year_obtained = db.Column(db.Integer, nullable=False)
    degree_number = db.Column(db.String(80), nullable=False)

    user = db.relationship("User", back_populates="professional_exam")


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)
