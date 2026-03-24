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


class ContractType(enum.Enum):
    pedagogue = "pedagogue"
    assistant_in_educational_and_training_work = "assistant in educational and training work"
    employee_according_to_the_labour_code = "employee according to the Labour Code"


class TeacherClassification(enum.Enum):
    trainee = "Trainee"
    teacher_i = "Teacher I"
    teacher_ii = "Teacher II"
    master_teacher = "Master Teacher"
    research_teacher = "Research Teacher"


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
    contracts = db.relationship("Contract", back_populates="user", cascade="all, delete-orphan")

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


class LegalEntity(db.Model):
    __tablename__ = "legal_entities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    om_id = db.Column(db.String(6), nullable=False)

    places_of_work = db.relationship("PlaceOfWork", back_populates="legal_entity", cascade="all, delete-orphan")
    contracts = db.relationship("Contract", back_populates="employer")


class PlaceOfWork(db.Model):
    __tablename__ = "places_of_work"

    id = db.Column(db.Integer, primary_key=True)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey("legal_entities.id"), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    legal_entity = db.relationship("LegalEntity", back_populates="places_of_work")
    contracts = db.relationship("Contract", back_populates="place_of_work")


class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contract_type = db.Column(db.Enum(ContractType), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    certificate_of_good_conduct_number = db.Column(db.String(64), nullable=True)
    certificate_of_good_conduct_date = db.Column(db.Date, nullable=True)
    job_title = db.Column(db.String(120), nullable=False)
    working_hours_per_week = db.Column(db.Integer, nullable=False)
    teacher_classification = db.Column(db.Enum(TeacherClassification), nullable=True)
    classification_start_date = db.Column(db.Date, nullable=True)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey("legal_entities.id"), nullable=False)
    place_of_work_id = db.Column(db.Integer, db.ForeignKey("places_of_work.id"), nullable=False)

    user = db.relationship("User", back_populates="contracts")
    employer = db.relationship("LegalEntity", back_populates="contracts")
    place_of_work = db.relationship("PlaceOfWork", back_populates="contracts")


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)
