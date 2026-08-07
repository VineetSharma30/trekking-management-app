from flask import Blueprint, render_template, flash, redirect, url_for, abort, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from .utils import redirect_dashboard
from models import Booking, Trek, User, db

user_bp = Blueprint("user", __name__)

@user_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    total_bookings = Booking.query.filter_by(user_id=current_user.id).count()

    upcoming_treks = Booking.query.filter_by(
        user_id=current_user.id,
        status="booked"
    ).count()

    completed_treks = Booking.query.filter_by(
        user_id=current_user.id,
        status="completed"
    ).count()

    open_treks = (
        Trek.query
        .filter(
            Trek.status == "open",
            Trek.available_slots > 0
        )
        .order_by(Trek.start_date.asc())
        .limit(5)
        .all()
    )

    recent_bookings = (
        Booking.query
        .filter_by(user_id=current_user.id)
        .order_by(Booking.booking_date.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "user/dashboard.html",
        total_bookings=total_bookings,
        upcoming_treks=upcoming_treks,
        completed_treks=completed_treks,
        open_treks=open_treks,
        recent_bookings=recent_bookings
    )


@user_bp.route("/treks")
@login_required
def browse_treks():
    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    location = request.args.get("location", "").strip()

    query = Trek.query.filter(
        Trek.status == "open",
        Trek.available_slots > 0
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

    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)

    if location:
        query = query.filter(
            Trek.location.ilike(f"%{location}%")
        )

    treks = (
        query
        .order_by(Trek.start_date.asc())
        .all()
    )

    booked_trek_ids = {
        booking.trek_id
        for booking in Booking.query.filter(
            Booking.user_id == current_user.id,
            Booking.status != "cancelled"
        ).all()
    }

    return render_template(
        "user/browse_treks.html",
        treks=treks,
        search=search,
        difficulty=difficulty,
        location=location,
        booked_trek_ids=booked_trek_ids
    )

@user_bp.route("/treks/<int:trek_id>")
@login_required
def trek_details(trek_id):

    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    trek = db.session.get(Trek, trek_id)
    if trek is None:
        abort(404)

    already_booked = (
        Booking.query.filter(
            Booking.user_id == current_user.id,
            Booking.trek_id == trek.id,
            Booking.status != "cancelled"
        ).first()
        is not None
    )

    return render_template(
        "user/trek_details.html",
        trek=trek,
        already_booked=already_booked
    )


@user_bp.route("/treks/<int:trek_id>/payment", methods=["GET", "POST"])
@login_required
def payment(trek_id):

    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    trek = db.session.get(Trek, trek_id)

    if trek is None:
        abort(404)

    if trek.status != "open":
        flash("This trek is not open for booking.", "danger")
        return redirect(url_for("user.browse_treks"))

    if trek.available_slots <= 0:
        flash("No slots available.", "danger")
        return redirect(url_for("user.trek_details", trek_id=trek.id))

    existing_booking = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.trek_id == trek.id,
        Booking.status != "cancelled"
    ).first()

    if existing_booking:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("user.my_bookings"))

    if request.method == "POST":

        booking = Booking(
            user_id=current_user.id,
            trek_id=trek.id,
            status="booked",
            payment_status="paid"
        )

        trek.available_slots -= 1

        db.session.add(booking)
        db.session.commit()

        flash("Payment successful. Trek booked successfully.", "success")

        return redirect(url_for("user.my_bookings"))

    return render_template(
        "user/payment.html",
        trek=trek
    )


@user_bp.route("/bookings")
@login_required
def my_bookings():

    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    search = request.args.get("search", "").strip()

    query = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.status == "booked"
    )

    if search:
        if search.isdigit():
            query = query.filter(
                Booking.id == int(search)
            )
        else:
            query = (
                query
                .join(Booking.trek)
                .filter(
                    Trek.name.ilike(f"%{search}%")
                )
            )

    bookings = (
        query
        .order_by(Booking.booking_date.desc())
        .all()
    )

    return render_template(
        "user/my_bookings.html",
        bookings=bookings,
        search=search
    )


@user_bp.route("/bookings/<int:booking_id>")
@login_required
def booking_details(booking_id):

    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    booking = db.session.get(Booking, booking_id)

    if booking is None:
        abort(404)

    if booking.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("user.my_bookings"))

    return render_template(
        "user/booking_details.html",
        booking=booking
    )


@user_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):

    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    booking = db.session.get(Booking, booking_id)

    if booking is None:
        abort(404)

    if booking.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("user.my_bookings"))

    if booking.status != "booked":
        flash("This booking cannot be cancelled.", "warning")
        return redirect(
            url_for(
                "user.booking_details",
                booking_id=booking.id
            )
        )
    
    if booking.trek.status != "open":
        flash("This booking cannot be cancelled after the trek has started or closed.", "warning")
        return redirect(
            url_for(
                "user.booking_details",
                booking_id=booking.id
            )
        )

    booking.status = "cancelled"
    booking.payment_status = "refunded"
    booking.trek.available_slots += 1

    db.session.commit()

    flash("Booking cancelled successfully.", "success")

    return redirect(url_for("user.my_bookings"))


@user_bp.route("/history")
@login_required
def booking_history():

    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "all")

    query = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.status.in_(["completed", "cancelled"])
    )

    if status != "all":
        query = query.filter(
            Booking.status == status
        )

    if search:
        if search.isdigit():
            query = query.filter(
                Booking.id == int(search)
            )
        else:
            query = (
                query
                .join(Booking.trek)
                .filter(
                    Trek.name.ilike(f"%{search}%")
                )
            )

    bookings = (
        query
        .order_by(Booking.booking_date.desc())
        .all()
    )

    return render_template(
        "user/history.html",
        bookings=bookings,
        search=search,
        status=status
    )


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    total_bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).count()

    if request.method == "POST":

        full_name = request.form.get("full_name","").strip()
        email = request.form.get("email","").strip()
        phone = request.form.get("phone", "").strip()

        if not full_name:
            flash("Full name is required.", "danger")
            return redirect(url_for("user.profile"))

        if not email:
            flash("Email is required.", "danger")
            return redirect(url_for("user.profile"))

        existing_user = (
            User.query.filter(
                User.email == email,
                User.id != current_user.id
            ).first()
        )

        if existing_user:
            flash("Email already exists.", "danger")
        else:
            current_user.full_name = full_name
            current_user.email = email
            current_user.phone = phone

            db.session.commit()

            flash("Profile updated successfully.", "success")

            return redirect(url_for("user.profile"))

    return render_template(
        "user/profile.html",
        total_bookings=total_bookings
    )
