from flask import Blueprint, render_template, flash, url_for, redirect, abort, request
from flask_login import login_required, current_user
from .utils import redirect_dashboard
from models import Trek, Booking, User, db
from sqlalchemy import or_

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "staff":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    assigned_treks = (
        Trek.query
        .filter_by(assigned_staff_id=current_user.id)
        .order_by(Trek.start_date.asc())
        .all()
    )

    total_participants = sum(
        len(trek.bookings)
        for trek in assigned_treks
    )

    open_treks = sum(
        1 for trek in assigned_treks
        if trek.status == "open"
    )

    return render_template(
        "staff/dashboard.html",
        assigned_treks=assigned_treks,
        total_participants=total_participants,
        open_treks=open_treks
    )


@staff_bp.route("/treks")
@login_required
def my_treks():

    if current_user.role != "staff":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    search = request.args.get("search", "").strip()

    query = Trek.query.filter(
        Trek.assigned_staff_id == current_user.id
    )

    if search:
        if search.isdigit():
            query = query.filter(Trek.id == int(search))
        else:
            query = query.filter(
                or_(
                    Trek.name.ilike(f"%{search}%"),
                    Trek.location.ilike(f"%{search}%")
                )
            )

    treks = query.order_by(Trek.start_date.asc()).all()

    return render_template(
        "staff/my_treks.html",
        treks=treks,
        search=search
    )


@staff_bp.route("/treks/<int:trek_id>", methods=["GET", "POST"])
@login_required
def manage_trek(trek_id):

    if current_user.role != "staff":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    trek = db.session.get(Trek, trek_id)
    if trek is None:
        abort(404)

    if trek.assigned_staff_id != current_user.id:
        flash("You are not assigned to this trek.", "danger")
        return redirect(url_for("staff.my_treks"))

    booked_count = len(trek.bookings)
    max_available_slots = trek.total_slots - booked_count

    if request.method == "POST":

        action = request.form.get("action")
        allowed_transitions = {
            "open": "started",
            "started": "ongoing",
            "ongoing": "completed"
        }

        if action:
            if allowed_transitions.get(trek.status) != action:
                flash("Invalid status transition.", "danger")
                return redirect(url_for("staff.manage_trek", trek_id=trek.id))

            trek.status = action

        else :
            trek.status = request.form["status"]

            try:
                available_slots = int(request.form["available_slots"])
            except ValueError:
                flash("Invalid slot value.", "danger")
                return redirect(
                    url_for("staff.manage_trek", trek_id=trek.id)
                )

            if available_slots < 0 or available_slots > max_available_slots:
                flash(f"Available slots must be between 0 and {max_available_slots}.","danger")
                return redirect(url_for("staff.manage_trek", trek_id=trek.id))

            trek.available_slots = available_slots
           
        db.session.commit()
        flash("Trek updated successfully.", "success")

        return redirect(url_for("staff.manage_trek", trek_id=trek.id))

    return render_template(
        "staff/manage_trek.html",
        trek=trek,
        max_available_slots=max_available_slots
    )


@staff_bp.route("/participants")
@login_required
def participants():

    if current_user.role != "staff":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    search = request.args.get("search", "").strip()

    query = (
        Booking.query
        .join(Booking.user)
        .join(Booking.trek)
        .filter(
            Trek.assigned_staff_id == current_user.id
        )
    )
    if search :
        if search.isdigit():
            query = query.filter(
                or_(
                    Booking.id == int(search),
                    User.id == int(search)
                )
            )
        else:
            query = query.filter(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    Trek.name.ilike(f"%{search}%")
                )
            )

    bookings = (
        query
        .order_by(Booking.booking_date.desc())
        .all()
    )

    return render_template(
        "staff/participants.html",
        bookings=bookings,
        search=search
    )


@staff_bp.route("/bookings/<int:booking_id>/complete", methods=["POST"])
@login_required
def complete_booking(booking_id):

    if current_user.role != "staff":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    booking = db.session.get(Booking, booking_id)
    if booking is None:
        abort(404)

    if booking.trek.assigned_staff_id != current_user.id:
        flash("You are not assigned to this trek.", "danger")
        return redirect(url_for("staff.dashboard"))

    if booking.status != "booked":
        flash("Booking is already processed.", "warning")
        return redirect(
            url_for(
                "staff.manage_trek",
                trek_id=booking.trek.id
            )
        )

    booking.status = "completed"

    db.session.commit()
    flash("Participant marked as completed.", "success")

    return redirect(
        url_for("staff.manage_trek", trek_id=booking.trek.id)
    )


@staff_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if current_user.role != "staff":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    assigned_trek_count = (
        Trek.query
        .filter_by(assigned_staff_id=current_user.id)
        .count()
    )

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        if not full_name:
            flash("Full name is required.", "danger")
            return redirect(url_for("staff.profile"))

        if not email:
            flash("Email is required.", "danger")
            return redirect(url_for("staff.profile"))

        existing_user = (
            User.query
            .filter(
                User.email == email,
                User.id != current_user.id
            )
            .first()
        )

        if existing_user:
            flash("Email already exists.", "danger")
            return redirect(url_for("staff.profile"))

        current_user.full_name = full_name
        current_user.email = email
        current_user.phone = phone

        db.session.commit()
        flash("Profile updated successfully.", "success")

        return redirect(url_for("staff.profile"))

    return render_template(
        "staff/profile.html",
        assigned_trek_count=assigned_trek_count
    )