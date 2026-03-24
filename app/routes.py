from datetime import datetime
from functools import wraps

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import db
from .models import (
    Dependent,
    EducationalQualification,
    Gender,
    ProfessionalExam,
    User,
    UserPrivilege,
    UserProfile,
    parse_iso_date,
)


MANAGEABLE_PRIVILEGES = (UserPrivilege.employee, UserPrivilege.hr, UserPrivilege.ceo, UserPrivilege.developer)

PROFILE_COMPLETION_FIELDS = (
    "full_name",
    "name_at_birth",
    "date_of_birth",
    "place_of_birth",
    "gender",
    "mothers_maiden_name",
    "citizenships",
    "social_security_number",
    "tax_number",
    "education_number",
    "teacher_id_card_number",
    "permanent_residence",
    "phone_number",
    "bank_account_number",
    "marital_status",
)


def _profile_completion_percentage(profile: UserProfile | None) -> int:
    if profile is None:
        return 0

    completed = sum(1 for field in PROFILE_COMPLETION_FIELDS if getattr(profile, field))
    return round((completed / len(PROFILE_COMPLETION_FIELDS)) * 100)


def _profile_status_label(profile: UserProfile | None) -> str:
    completion_percentage = _profile_completion_percentage(profile)
    if completion_percentage == 100:
        return "Complete"
    return f"{completion_percentage}% complete"


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _validate_digit_field(label: str, value: str | None, length: int) -> str | None:
    normalized = _normalize_optional_text(value)
    if not normalized:
        return None
    if not normalized.isdigit() or len(normalized) != length:
        return f"{label} must be exactly {length} digits."
    return None


def _save_profile_from_form(profile: UserProfile) -> list[str]:
    social_security_number = _normalize_optional_text(request.form.get("social_security_number"))
    tax_number = _normalize_optional_text(request.form.get("tax_number"))
    education_number = _normalize_optional_text(request.form.get("education_number"))

    errors = [
        _validate_digit_field("Social security number", social_security_number, 9),
        _validate_digit_field("Tax number", tax_number, 10),
        _validate_digit_field("Education number", education_number, 11),
    ]
    errors = [err for err in errors if err]
    if errors:
        return errors

    profile.full_name = _normalize_optional_text(request.form.get("full_name"))
    profile.name_at_birth = _normalize_optional_text(request.form.get("name_at_birth"))
    profile.date_of_birth = parse_iso_date(request.form.get("date_of_birth"))
    profile.place_of_birth = _normalize_optional_text(request.form.get("place_of_birth"))
    gender_value = _normalize_optional_text(request.form.get("gender"))
    profile.gender = Gender(gender_value) if gender_value else None
    profile.mothers_maiden_name = _normalize_optional_text(request.form.get("mothers_maiden_name"))
    profile.citizenships = _normalize_optional_text(request.form.get("citizenships"))
    profile.social_security_number = social_security_number
    profile.tax_number = tax_number
    profile.education_number = education_number
    profile.teacher_id_card_number = _normalize_optional_text(request.form.get("teacher_id_card_number"))
    profile.permanent_residence = _normalize_optional_text(request.form.get("permanent_residence"))
    profile.temporary_address = _normalize_optional_text(request.form.get("temporary_address"))
    profile.phone_number = _normalize_optional_text(request.form.get("phone_number"))
    profile.bank_account_number = _normalize_optional_text(request.form.get("bank_account_number"))
    profile.marital_status = _normalize_optional_text(request.form.get("marital_status"))
    profile.disability = _normalize_optional_text(request.form.get("disability"))
    return []


def _render_profile_editor(profile: UserProfile, target_user: User, *, manager_mode: bool = False):
    return render_template(
        "profile.html",
        profile=profile,
        genders=Gender,
        manager_mode=manager_mode,
        target_user=target_user,
    )


def _can_manage_privileges(user: User) -> bool:
    return user.is_authenticated and user.privilege in {UserPrivilege.hr, UserPrivilege.ceo}


def privilege_manager_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(*args, **kwargs):
        if not _can_manage_privileges(current_user):
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped_view


def init_routes(app):
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not email or not username or not password:
                flash("Email, username and password are required.", "error")
                return render_template("register.html")

            if User.query.filter((User.email == email) | (User.username == username)).first():
                flash("Email or username already exists.", "error")
                return render_template("register.html")

            user = User(email=email, username=username, privilege=UserPrivilege.employee)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            profile = UserProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()

            login_user(user)
            flash("Registration successful. Your privilege is set to employee until HR or the CEO updates it.", "success")
            return redirect(url_for("edit_profile"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            login_identifier = request.form.get("login", "").strip()
            password = request.form.get("password", "")

            user = User.query.filter(
                (User.email == login_identifier.lower()) | (User.username == login_identifier)
            ).first()

            if not user or not user.check_password(password):
                flash("Invalid credentials.", "error")
                return render_template("login.html")

            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out.", "success")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template(
            "dashboard.html",
            can_manage_privileges=_can_manage_privileges(current_user),
            can_manage_user_profiles=_can_manage_privileges(current_user),
            profile_status_label=_profile_status_label(current_user.profile),
        )

    @app.route("/users/privileges", methods=["GET", "POST"])
    @privilege_manager_required
    def manage_privileges():
        if request.method == "POST":
            user_id = request.form.get("user_id", type=int)
            privilege_raw = request.form.get("privilege", UserPrivilege.employee.value)
            user = db.session.get(User, user_id)

            if user is None:
                flash("User not found.", "error")
                return redirect(url_for("manage_privileges"))

            try:
                privilege = UserPrivilege(privilege_raw)
            except ValueError:
                flash("Invalid privilege selected.", "error")
                return redirect(url_for("manage_privileges"))

            if privilege not in MANAGEABLE_PRIVILEGES:
                flash("That privilege cannot be assigned here.", "error")
                return redirect(url_for("manage_privileges"))

            user.privilege = privilege
            db.session.commit()
            flash(f"Updated {user.username} to {privilege.value} privilege.", "success")
            return redirect(url_for("manage_privileges"))

        users = User.query.order_by(User.id.asc()).all()
        return render_template(
            "manage_privileges.html",
            users=users,
            privileges=MANAGEABLE_PRIVILEGES,
        )

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def edit_profile():
        profile = current_user.profile or UserProfile(user_id=current_user.id)
        if request.method == "POST":
            errors = _save_profile_from_form(profile)
            if errors:
                for err in errors:
                    flash(err, "error")
                return _render_profile_editor(profile, current_user)

            db.session.add(profile)
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(url_for("dashboard"))

        return _render_profile_editor(profile, current_user)

    @app.route("/users/profiles")
    @privilege_manager_required
    def manage_user_profiles():
        users = User.query.order_by(User.username.asc()).all()
        return render_template("manage_user_profiles.html", users=users)

    @app.route("/users/<int:user_id>/profile", methods=["GET", "POST"])
    @privilege_manager_required
    def edit_user_profile(user_id: int):
        target_user = db.session.get(User, user_id)
        if target_user is None:
            flash("User not found.", "error")
            return redirect(url_for("manage_user_profiles"))

        profile = target_user.profile or UserProfile(user_id=target_user.id)
        if request.method == "POST":
            errors = _save_profile_from_form(profile)
            if errors:
                for err in errors:
                    flash(err, "error")
                return _render_profile_editor(profile, target_user, manager_mode=True)

            db.session.add(profile)
            db.session.commit()
            flash(f"Updated profile for {target_user.username}.", "success")
            return redirect(url_for("manage_user_profiles"))

        return _render_profile_editor(profile, target_user, manager_mode=True)

    @app.route("/dependents/add", methods=["GET", "POST"])
    @login_required
    def add_dependent():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            social_security_number = request.form.get("social_security_number", "").strip()
            if not name:
                flash("Dependent name is required.", "error")
                return render_template("dependent_form.html")
            validation_error = _validate_digit_field(
                "Dependent social security number", social_security_number, 9
            )
            if validation_error:
                flash(validation_error, "error")
                return render_template("dependent_form.html")

            dependent = Dependent(
                user_id=current_user.id,
                name=name,
                date_of_birth=parse_iso_date(request.form.get("date_of_birth")),
                social_security_number=social_security_number,
                dependency_start=parse_iso_date(request.form.get("dependency_start")),
                disability=request.form.get("disability"),
            )
            db.session.add(dependent)
            db.session.commit()
            flash("Dependent added.", "success")
            return redirect(url_for("dashboard"))

        return render_template("dependent_form.html")

    @app.route("/qualifications/add", methods=["GET", "POST"])
    @login_required
    def add_qualification():
        if request.method == "POST":
            try:
                year_obtained = int(request.form.get("year_obtained", "0"))
            except ValueError:
                flash("Year obtained must be a number.", "error")
                return render_template("qualification_form.html")

            qualification = EducationalQualification(
                user_id=current_user.id,
                level_or_type=request.form.get("level_or_type"),
                qualification_name=request.form.get("qualification_name"),
                institution_name=request.form.get("institution_name"),
                degree_number=request.form.get("degree_number"),
                year_obtained=year_obtained,
                highest=request.form.get("highest") == "on",
            )
            if qualification.highest:
                EducationalQualification.query.filter_by(user_id=current_user.id, highest=True).update(
                    {EducationalQualification.highest: False}
                )
            db.session.add(qualification)
            db.session.commit()
            flash("Educational qualification added.", "success")
            return redirect(url_for("dashboard"))

        return render_template("qualification_form.html")

    @app.route("/professional-exam", methods=["GET", "POST"])
    @login_required
    def professional_exam():
        exam = current_user.professional_exam or ProfessionalExam(user_id=current_user.id)
        if request.method == "POST":
            qualification_name = request.form.get("qualification_name", "").strip()
            degree_number = request.form.get("degree_number", "").strip()
            year_raw = request.form.get("year_obtained", "").strip()

            if not qualification_name and not degree_number and not year_raw:
                if exam.id:
                    db.session.delete(exam)
                    db.session.commit()
                flash("Professional exam removed.", "success")
                return redirect(url_for("dashboard"))

            try:
                year_obtained = int(year_raw)
                if year_obtained < 1900 or year_obtained > datetime.now().year + 1:
                    raise ValueError
            except ValueError:
                flash("Year obtained is invalid.", "error")
                return render_template("professional_exam_form.html", exam=exam)

            exam.qualification_name = qualification_name
            exam.degree_number = degree_number
            exam.year_obtained = year_obtained
            db.session.add(exam)
            db.session.commit()
            flash("Professional exam saved.", "success")
            return redirect(url_for("dashboard"))

        return render_template("professional_exam_form.html", exam=exam)
