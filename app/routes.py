from datetime import datetime
from functools import wraps

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import db
from .models import (
    Contract,
    ContractType,
    Dependent,
    DependentType,
    EducationalQualification,
    Gender,
    Leadership,
    LeadershipPosition,
    LegalEntity,
    PlaceOfWork,
    ProfessionalExam,
    MaritalStatus,
    TeacherClassification,
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
    marital_status_value = _normalize_optional_text(request.form.get("marital_status"))
    profile.marital_status = MaritalStatus(marital_status_value) if marital_status_value else None
    profile.disability = _normalize_optional_text(request.form.get("disability"))
    return []


def _render_profile_editor(profile: UserProfile, target_user: User, *, manager_mode: bool = False):
    return render_template(
        "profile.html",
        profile=profile,
        genders=Gender,
        marital_statuses=MaritalStatus,
        manager_mode=manager_mode,
        target_user=target_user,
    )




def _validate_om_id(value: str | None) -> str | None:
    normalized = _normalize_optional_text(value)
    if not normalized or not normalized.isdigit() or len(normalized) != 6:
        return "OM id must be exactly 6 digits."
    return None


def _contract_place_label(place: PlaceOfWork) -> str:
    return f"{place.legal_entity.name} - {place.address}"


def _save_contract_from_form(contract: Contract) -> list[str]:
    contract_type_raw = _normalize_optional_text(request.form.get("contract_type"))
    teacher_classification_raw = _normalize_optional_text(request.form.get("teacher_classification"))
    legal_entity_id = request.form.get("legal_entity_id", type=int)
    place_of_work_id = request.form.get("place_of_work_id", type=int)

    if not contract_type_raw:
        return ["Contract type is required."]

    try:
        contract.contract_type = ContractType(contract_type_raw)
    except ValueError:
        return ["Invalid contract type selected."]

    if not legal_entity_id:
        return ["Employer is required."]
    if not place_of_work_id:
        return ["Place of work is required."]

    contract.legal_entity_id = legal_entity_id
    contract.place_of_work_id = place_of_work_id

    contract.start_date = parse_iso_date(request.form.get("start_date"))
    contract.end_date = parse_iso_date(request.form.get("end_date"))
    contract.certificate_of_good_conduct_number = _normalize_optional_text(
        request.form.get("certificate_of_good_conduct_number")
    )
    contract.certificate_of_good_conduct_date = parse_iso_date(request.form.get("certificate_of_good_conduct_date"))
    contract.job_title = _normalize_optional_text(request.form.get("job_title"))
    contract.working_hours_per_week = request.form.get("working_hours_per_week", type=int)
    contract.teacher_classification = (
        TeacherClassification(teacher_classification_raw) if teacher_classification_raw else None
    )
    contract.classification_start_date = parse_iso_date(request.form.get("classification_start_date"))

    errors = []
    if contract.start_date is None:
        errors.append("Start date is required.")
    if not contract.job_title:
        errors.append("Job title is required.")
    if contract.working_hours_per_week is None:
        errors.append("Working hours per week is required.")
    elif contract.working_hours_per_week < 1:
        errors.append("Working hours per week must be greater than 0.")

    if contract.end_date and contract.start_date and contract.end_date < contract.start_date:
        errors.append("End date cannot be earlier than the start date.")

    if contract.place_of_work_id and contract.legal_entity_id:
        place = db.session.get(PlaceOfWork, contract.place_of_work_id)
        if place is None:
            errors.append("Selected place of work does not exist.")
        elif place.legal_entity_id != contract.legal_entity_id:
            errors.append("Selected place of work does not belong to the selected employer.")

    return errors


def _save_leadership_from_form(leadership: Leadership) -> list[str]:
    legal_entity_id = request.form.get("legal_entity_id", type=int)
    contract_id = request.form.get("contract_id", type=int)
    position_value = request.form.get("position")

    leadership.legal_entity_id = legal_entity_id
    leadership.contract_id = contract_id
    leadership.position = LeadershipPosition(position_value) if position_value in {item.value for item in LeadershipPosition} else None
    leadership.start_date = parse_iso_date(request.form.get("start_date"))
    leadership.end_date = parse_iso_date(request.form.get("end_date"))

    errors = []
    if not legal_entity_id:
        errors.append("Legal entity is required.")
    if not contract_id:
        errors.append("Contract is required.")
    if leadership.position is None:
        errors.append("Leadership position is required.")
    if leadership.start_date is None:
        errors.append("Start date is required.")
    if leadership.end_date and leadership.start_date and leadership.end_date < leadership.start_date:
        errors.append("End date cannot be earlier than the start date.")

    if contract_id:
        contract = db.session.get(Contract, contract_id)
        if contract is None:
            errors.append("Selected contract does not exist.")
        elif legal_entity_id and contract.legal_entity_id != legal_entity_id:
            errors.append("Selected contract does not belong to the selected legal entity.")

    return errors

def _can_manage_privileges(user: User) -> bool:
    return user.is_authenticated and user.privilege in {UserPrivilege.hr, UserPrivilege.ceo}


def _can_assign_privileges(user: User) -> bool:
    return user.is_authenticated and user.privilege in {UserPrivilege.hr, UserPrivilege.ceo, UserPrivilege.developer}


def privilege_manager_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(*args, **kwargs):
        if not _can_manage_privileges(current_user):
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped_view




def privilege_assignment_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(*args, **kwargs):
        if not _can_assign_privileges(current_user):
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
            can_assign_privileges=_can_assign_privileges(current_user),
            can_manage_user_profiles=_can_manage_privileges(current_user),
            can_manage_leadership=_can_manage_privileges(current_user),
            profile_status_label=_profile_status_label(current_user.profile),
        )

    @app.route("/users/privileges", methods=["GET", "POST"])
    @privilege_assignment_required
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

    @app.route("/password", methods=["GET", "POST"])
    @login_required
    def change_password():
        if request.method == "POST":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            new_password_confirm = request.form.get("new_password_confirm", "")

            if not current_user.check_password(current_password):
                flash("Current password is incorrect.", "error")
                return render_template("change_password.html")

            if not new_password:
                flash("New password is required.", "error")
                return render_template("change_password.html")

            if new_password != new_password_confirm:
                flash("New password and confirmation do not match.", "error")
                return render_template("change_password.html")

            current_user.set_password(new_password)
            db.session.add(current_user)
            db.session.commit()
            flash("Password updated successfully.", "success")
            return redirect(url_for("dashboard"))

        return render_template("change_password.html")

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
            dependent_type_raw = request.form.get("dependent_type", "").strip()
            social_security_number = request.form.get("social_security_number", "").strip()
            if not name:
                flash("Dependent name is required.", "error")
                return render_template("dependent_form.html", dependent_types=DependentType)
            if dependent_type_raw not in {item.value for item in DependentType}:
                flash("Dependent type is required.", "error")
                return render_template("dependent_form.html", dependent_types=DependentType)
            validation_error = _validate_digit_field(
                "Dependent social security number", social_security_number, 9
            )
            if validation_error:
                flash(validation_error, "error")
                return render_template("dependent_form.html", dependent_types=DependentType)

            dependent = Dependent(
                user_id=current_user.id,
                name=name,
                dependent_type=DependentType(dependent_type_raw),
                date_of_birth=parse_iso_date(request.form.get("date_of_birth")),
                social_security_number=social_security_number,
                dependency_start=parse_iso_date(request.form.get("dependency_start")),
                disability=request.form.get("disability"),
            )
            db.session.add(dependent)
            db.session.commit()
            flash("Dependent added.", "success")
            return redirect(url_for("dashboard"))

        return render_template("dependent_form.html", dependent_types=DependentType)

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



    @app.route("/legal-entities", methods=["GET", "POST"])
    @privilege_manager_required
    def manage_legal_entities():
        editing_entity_id = request.args.get("edit", type=int)
        if request.method == "POST":
            entity_id = request.form.get("entity_id", type=int)
            name = _normalize_optional_text(request.form.get("name"))
            address = _normalize_optional_text(request.form.get("address"))
            om_id = _normalize_optional_text(request.form.get("om_id"))
            tax_number = _normalize_optional_text(request.form.get("tax_number"))

            if not name or not address or not tax_number:
                flash("Name, address, and tax number are required.", "error")
                return redirect(url_for("manage_legal_entities"))

            om_error = _validate_om_id(om_id)
            if om_error:
                flash(om_error, "error")
                return redirect(url_for("manage_legal_entities"))
            tax_error = _validate_digit_field("Tax number", tax_number, 10)
            if tax_error:
                flash(tax_error, "error")
                return redirect(url_for("manage_legal_entities"))

            entity = db.session.get(LegalEntity, entity_id) if entity_id else LegalEntity()
            if entity is None:
                flash("Legal entity not found.", "error")
                return redirect(url_for("manage_legal_entities"))

            entity.name = name
            entity.address = address
            entity.om_id = om_id
            entity.tax_number = tax_number
            db.session.add(entity)
            db.session.commit()
            flash("Legal entity updated." if entity_id else "Legal entity saved.", "success")
            return redirect(url_for("manage_legal_entities"))

        entities = LegalEntity.query.order_by(LegalEntity.name.asc()).all()
        editing_entity = None
        if editing_entity_id:
            editing_entity = db.session.get(LegalEntity, editing_entity_id)
            if editing_entity is None:
                flash("Legal entity not found.", "error")
                return redirect(url_for("manage_legal_entities"))
        return render_template("manage_legal_entities.html", entities=entities, editing_entity=editing_entity)

    @app.route("/places-of-work", methods=["GET", "POST"])
    @privilege_manager_required
    def manage_places_of_work():
        editing_place_id = request.args.get("edit", type=int)
        if request.method == "POST":
            place_id = request.form.get("place_id", type=int)
            legal_entity_id = request.form.get("legal_entity_id", type=int)
            address = _normalize_optional_text(request.form.get("address"))

            if not legal_entity_id or not address:
                flash("Employer and address are required.", "error")
                return redirect(url_for("manage_places_of_work"))

            if db.session.get(LegalEntity, legal_entity_id) is None:
                flash("Selected employer does not exist.", "error")
                return redirect(url_for("manage_places_of_work"))

            place = db.session.get(PlaceOfWork, place_id) if place_id else PlaceOfWork()
            if place is None:
                flash("Place of work not found.", "error")
                return redirect(url_for("manage_places_of_work"))

            place.legal_entity_id = legal_entity_id
            place.address = address
            db.session.add(place)
            db.session.commit()
            flash("Place of work updated." if place_id else "Place of work saved.", "success")
            return redirect(url_for("manage_places_of_work"))

        entities = LegalEntity.query.order_by(LegalEntity.name.asc()).all()
        places = PlaceOfWork.query.join(LegalEntity).order_by(LegalEntity.name.asc(), PlaceOfWork.address.asc()).all()
        editing_place = None
        if editing_place_id:
            editing_place = db.session.get(PlaceOfWork, editing_place_id)
            if editing_place is None:
                flash("Place of work not found.", "error")
                return redirect(url_for("manage_places_of_work"))
        return render_template(
            "manage_places_of_work.html",
            entities=entities,
            places=places,
            editing_place=editing_place,
        )

    @app.route("/contracts")
    @privilege_manager_required
    def manage_contracts():
        users = User.query.order_by(User.username.asc()).all()
        return render_template("manage_contracts.html", users=users)

    @app.route("/users/<int:user_id>/contracts/new", methods=["GET", "POST"])
    @privilege_manager_required
    def create_contract(user_id: int):
        target_user = db.session.get(User, user_id)
        if target_user is None:
            flash("User not found.", "error")
            return redirect(url_for("manage_contracts"))

        contract = Contract(user_id=target_user.id)
        if request.method == "POST":
            errors = _save_contract_from_form(contract)
            if errors:
                for err in errors:
                    flash(err, "error")
            else:
                db.session.add(contract)
                db.session.commit()
                flash(f"Contract created for {target_user.username}.", "success")
                return redirect(url_for("manage_contracts"))

        entities = LegalEntity.query.order_by(LegalEntity.name.asc()).all()
        places = PlaceOfWork.query.join(LegalEntity).order_by(LegalEntity.name.asc(), PlaceOfWork.address.asc()).all()
        return render_template(
            "contract_form.html",
            target_user=target_user,
            contract=contract,
            contract_types=ContractType,
            teacher_classifications=TeacherClassification,
            legal_entities=entities,
            places_of_work=places,
            place_label_fn=_contract_place_label,
            mode="create",
        )

    @app.route("/contracts/<int:contract_id>/edit", methods=["GET", "POST"])
    @privilege_manager_required
    def edit_contract(contract_id: int):
        contract = db.session.get(Contract, contract_id)
        if contract is None:
            flash("Contract not found.", "error")
            return redirect(url_for("manage_contracts"))

        if request.method == "POST":
            errors = _save_contract_from_form(contract)
            if errors:
                for err in errors:
                    flash(err, "error")
            else:
                db.session.add(contract)
                db.session.commit()
                flash(f"Contract updated for {contract.user.username}.", "success")
                return redirect(url_for("manage_contracts"))

        entities = LegalEntity.query.order_by(LegalEntity.name.asc()).all()
        places = PlaceOfWork.query.join(LegalEntity).order_by(LegalEntity.name.asc(), PlaceOfWork.address.asc()).all()
        return render_template(
            "contract_form.html",
            target_user=contract.user,
            contract=contract,
            contract_types=ContractType,
            teacher_classifications=TeacherClassification,
            legal_entities=entities,
            places_of_work=places,
            place_label_fn=_contract_place_label,
            mode="edit",
        )

    @app.route("/leadership", methods=["GET", "POST"])
    @privilege_manager_required
    def manage_leadership():
        editing_leadership_id = request.args.get("edit", type=int)
        if request.method == "POST":
            leadership_id = request.form.get("leadership_id", type=int)
            leadership = db.session.get(Leadership, leadership_id) if leadership_id else Leadership()
            if leadership is None:
                flash("Leadership record not found.", "error")
                return redirect(url_for("manage_leadership"))

            errors = _save_leadership_from_form(leadership)
            if errors:
                for err in errors:
                    flash(err, "error")
                return redirect(url_for("manage_leadership", edit=leadership_id) if leadership_id else url_for("manage_leadership"))

            db.session.add(leadership)
            db.session.commit()
            flash("Leadership record updated." if leadership_id else "Leadership record saved.", "success")
            return redirect(url_for("manage_leadership"))

        legal_entities = LegalEntity.query.order_by(LegalEntity.name.asc()).all()
        contracts = (
            Contract.query.join(User)
            .join(LegalEntity)
            .order_by(LegalEntity.name.asc(), User.username.asc(), Contract.start_date.desc())
            .all()
        )
        leadership_positions = (
            Leadership.query.join(LegalEntity)
            .join(Contract)
            .order_by(LegalEntity.name.asc(), Leadership.start_date.desc(), Leadership.id.desc())
            .all()
        )
        editing_leadership = None
        if editing_leadership_id:
            editing_leadership = db.session.get(Leadership, editing_leadership_id)
            if editing_leadership is None:
                flash("Leadership record not found.", "error")
                return redirect(url_for("manage_leadership"))

        return render_template(
            "manage_leadership.html",
            legal_entities=legal_entities,
            contracts=contracts,
            leadership_positions=leadership_positions,
            editing_leadership=editing_leadership,
        )

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
