from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from .utils import redirect_dashboard
from models import Trek, User, Booking, StaffProfile
from extensions import db
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

# Dashboard
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "admin" :
            flash("Access denied.", "danger")
            return redirect_dashboard(current_user)

    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role="user").count()
    total_staff = User.query.filter_by(role="staff").count()
    total_bookings = Booking.query.count()

    recent_bookings = (
        Booking.query
        .order_by(Booking.booking_date.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_treks=total_treks,
        total_users=total_users, 
        total_staff=total_staff, 
        total_bookings=total_bookings,
        recent_bookings=recent_bookings
    )

 
# Trek
@admin_bp.route("/treks")
@login_required
def treks():

    if current_user.role != "admin":
            flash("Access denied.", "danger")
            return redirect_dashboard(current_user)

    search = request.args.get("search", "").strip()

    query = Trek.query

    if search:
        if search.isdigit():
            query = Trek.query.filter(Trek.id == int(search))
        else:
            query = Trek.query.filter(
                Trek.name.ilike(f"%{search}%")
            )
    
    treks = query.order_by(Trek.created_at.desc()).all()

    approved_staff = (
        User.query
        .join(StaffProfile)
        .filter(
            User.role == "staff",
            StaffProfile.approval_status == "approved"
        )
        .order_by(User.full_name)
        .all()
    )

    return render_template(
        "admin/treks.html",
        treks=treks,
        approved_staff=approved_staff,
        search=search
    )

    
# Create Trek
@admin_bp.route("/treks/create", methods=["GET", "POST"])
@login_required
def create_trek():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)
    
    if request.method == "POST":

        name = request.form["name"].strip()
        location = request.form["location"].strip()
        difficulty = request.form["difficulty"].lower().strip()

        duration_days = int(request.form["duration_days"])
        total_slots = int(request.form["total_slots"])

        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()

        description = request.form["description"].strip()

        price = float(request.form["price"])
        image_url = request.form["image_url"]

        # Ensure corrcet start and end date
        if start_date < datetime.today().date():
            flash("Start date cannot be in the past.", "danger")
            return render_template("admin/create_trek.html")

        if end_date < start_date:
            flash("End date cannot be before start date.", "danger")
            return render_template("admin/create_trek.html")
        
        # Ensure duration of trek
        if duration_days <= 0:
            flash("Duration must be greater than zero.", "danger")
            return render_template("admin/create_trek.html")
        
        # Ensure suffucient slots
        if total_slots <= 0:
            flash("Total slots must be greater than zero.", "danger")
            return render_template("admin/create_trek.html")

        
        # Create trek object
        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration_days=duration_days,
            total_slots=total_slots,
            available_slots=total_slots,
            start_date=start_date,
            end_date=end_date,
            description=description,
            price=price,
            image_url=image_url
        )

        try:
            # Add and commit trek to db session
            db.session.add(trek)
            db.session.commit()

            flash("Trek created successfully.", "success")
            return redirect(url_for("admin.treks"))

        except Exception as e:
            # Trek registration failed rollback to current transaction
            db.session.rollback()
            print(e)

            flash("Unable to create trek.", "danger")
            return render_template("admin/create_trek.html")
        
    return render_template("admin/create_trek.html")


# Edit Trek
@admin_bp.route("/treks/<int:trek_id>/edit", methods=["GET", "POST"])
@login_required
def edit_trek(trek_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    trek = db.session.get(Trek, trek_id)
    if trek is None:
        abort(404)

    if request.method == "POST":

        trek.name = request.form["name"].strip()
        trek.location = request.form["location"].strip()
        trek.difficulty = request.form["difficulty"].strip()

        trek.duration_days = int(request.form["duration_days"])
        trek.total_slots = int(request.form["total_slots"])

        trek.start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        trek.end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()

        trek.description = request.form["description"].strip()
        booked_slots = trek.total_slots - trek.available_slots

        # Ensure corrcet start and end date
        if trek.start_date < datetime.today().date():
            flash("Start date cannot be in the past.", "danger")
            return render_template("admin/create_trek.html")
        
        if trek.end_date < trek.start_date:
            flash("End date cannot be before start date.", "danger")
            return render_template("admin/edit_trek.html", trek=trek)
        
        # Ensure duration of trek
        if trek.duration_days <= 0:
            flash("Duration must be greater than zero.", "danger")
            return render_template("admin/edit_trek.html", trek=trek)
        
        # Ensure suffucient slots
        if trek.total_slots <= 0:
            flash("Total slots must be greater than zero.", "danger")
            return render_template("admin/edit_trek.html", trek=trek)
        if trek.total_slots < booked_slots:
            flash(f"Total slots cannot be less than {booked_slots}.", "danger")
            return render_template("admin/edit_trek.html", trek=trek)
        
        try:
            # Commit to db session
            db.session.commit()

            flash("Trek updated successfully.", "success")
            return redirect(url_for("admin.treks"))

        except Exception as e:
            # Trek registration failed rollback to current transaction
            db.session.rollback()
            print(e)

            flash("Unable to update trek.", "danger")
            return render_template(
                "admin/edit_trek.html",
                trek=trek
            )

    return render_template(
        "admin/edit_trek.html",
        trek=trek
    )


# Delete Trek
@admin_bp.route("/treks/<int:trek_id>/delete", methods=["POST"])
@login_required
def delete_trek(trek_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)
    
    trek = db.session.get(Trek, trek_id)
    if trek is None:
        abort(404)

    if trek.bookings:
        flash("This trek has bookings and cannot be deleted.", "danger")
        return redirect(url_for("admin.treks"))

    try:
        # Add andcommit trek to db session
        db.session.delete(trek)
        db.session.commit()
        flash("Trek deleted successfully.", "success")

    except Exception as e:
        # Trek registration failed rollback to current transaction
        db.session.rollback()
        print(e)
        flash("Unable to delete trek.", "danger")

    return redirect(url_for("admin.treks"))


# Staff
@admin_bp.route("/staff")
@login_required
def staff():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    all_staff = (
        User.query
        .filter(User.role == "staff")
        .order_by(User.created_at.desc()).all()
    )
    all_count = len(all_staff)
    pending = sum(
        1 for s in all_staff
        if s.staff_profile.approval_status == "pending"
    )
    approved = sum(
        1 for s in all_staff
        if s.staff_profile.approval_status == "approved"
        and s.status != "blacklisted"
    )
    blacklisted = sum(
        1 for s in all_staff
        if s.status == "blacklisted"
    )

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "all")

    query = (
        User.query
        .join(StaffProfile)
        .filter(User.role == "staff")
    )

    if search:
        if search.isdigit():
            query = query.filter(User.id == int(search))
        else:
            query = query.filter(
                User.full_name.ilike(f"%{search}%")
            )


    if status == "pending":
        query = query.filter(
            StaffProfile.approval_status == "pending"
        )

    elif status == "approved":
        query = query.filter(
            StaffProfile.approval_status == "approved",
            User.status != "blacklisted"
        )

    elif status == "blacklisted":
        query = query.filter(
            User.status == "blacklisted"
        )

    staff_members = (
        query
        .order_by(User.created_at.desc())
        .all()
    )

    return render_template(
        "admin/staff.html",
        staff_members=staff_members,
        status=status,
        all_count=all_count,
        pending=pending,
        approved=approved,
        blacklisted=blacklisted,
        search=search
    )


# Approve Staff
@admin_bp.route("/staff/<int:user_id>/approve", methods=["POST"])
@login_required
def approve_staff(user_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    staff = db.session.get(User, user_id)
    if staff is None:
        abort(404)
        
    if staff.role != "staff":
        flash("Invalid staff member.", "danger")
        return redirect(url_for("admin.staff"))

    try:

        # Approve the user role as staff
        staff.staff_profile.approval_status = "approved"
        staff.status = "active"

        db.session.commit()
        flash("Staff approved successfully.", "success")

    except Exception as e:

        db.session.rollback()
        print(e)
        flash("Unable to approve staff.", "danger")

    return redirect(url_for("admin.staff"))


# Reject Staff
@admin_bp.route("/staff/<int:user_id>/reject", methods=["POST"])
@login_required
def reject_staff(user_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    staff = db.session.get(User, user_id)
    if staff is None:
        abort(404)
        
    if staff.role != "staff":
        flash("Invalid staff member.", "danger")
        return redirect(url_for("admin.staff"))

    try:

        # Reject the user role as staff
        staff.staff_profile.approval_status = "rejected"
        staff.status = "inactive"

        db.session.commit()
        flash("Staff Rejected.", "success")

    except Exception as e:

        db.session.rollback()
        print(e)
        flash("Unable to reject staff.", "danger")

    return redirect(url_for("admin.staff"))


# Assign Staff to a trek
@admin_bp.route("/treks/<int:trek_id>/assign", methods=["GET", "POST"])
@login_required
def assign_staff(trek_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    trek = db.session.get(Trek, trek_id)
    if trek is None:
        abort(404)

    approved_staff = (
        User.query
        .join(User.staff_profile)
        .filter(
            User.role == "staff",
            StaffProfile.approval_status == "approved"
        ).all()
    )

    if request.method == "POST":

        staff_id = request.form["staff_id"]
        trek.assigned_staff_id = int(staff_id)

        db.session.commit()
        flash("Staff assigned successfully.", "success")
        return redirect(url_for("admin.treks"))

    return render_template(
        "admin/assign_staff.html",
        trek=trek,
        approved_staff=approved_staff,
    )


# Remove Staff from a trek
@admin_bp.route("/treks/<int:trek_id>/remove_staff", methods=["POST"])
@login_required
def remove_staff(trek_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    trek = db.session.get(Trek, trek_id)
    if trek is None:
        abort(404)

    trek.assigned_staff_id = None

    db.session.commit()
    flash("Staff removed from trek.", "success")

    return redirect(url_for("admin.treks"))


# Users
@admin_bp.route("/users")
@login_required
def users():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    search = request.args.get("search", "").strip()

    query = User.query.filter_by(role="user")

    if search:
        if search.isdigit():
            query = query.filter(User.id == int(search))
        else:
            query = query.filter(
                User.full_name.ilike(f"%{search}%")
            )

    users = (
        query
        .order_by(User.created_at.desc())
        .all()
    )

    return render_template(
        "admin/users.html",
        users=users,
        search=search
    )


# Blacklist users and staff
@admin_bp.route("/account/<int:user_id>/status", methods=["POST"])
@login_required
def change_account_status(user_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    user = db.session.get(User, user_id)
    if user is None:
        abort(404)    

    status = request.form["status"]
    next_page = request.form.get("next", "admin.users")

    if user.id == current_user.id:
        flash("You cannot blacklist your own account.", "danger")
        return redirect(url_for(next_page))

    try:

        user.status = status
        
        db.session.commit()
        flash("Account status updated successfully.", "success")

    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Unable to update account status.", "danger")

    return redirect(url_for(next_page))   


# Bookings
@admin_bp.route("/bookings")
@login_required
def bookings():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect_dashboard(current_user)

    query = Booking.query

    all_bookings = (
        Booking.query
        .order_by(Booking.booking_date.desc())
        .all()
    )

    all_count =  len(all_bookings)

    booked = sum(
        1 for b in all_bookings
        if b.status == "booked"
    )
    completed = sum(
        1 for b in all_bookings
        if b.status == "completed"
    )
    cancelled = sum(
        1 for b in all_bookings
        if b.status == "cancelled"
    )
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "all")


    if search:
        if search.isdigit():
            query = query.filter(Booking.id == int(search))
        else:
            query = (
                query
                .join(Booking.user)
                .join(Booking.trek)
                .filter(
                    or_(
                        User.full_name.ilike(f"%{search}%"),
                        Trek.name.ilike(f"%{search}%")
                    )
                )
            )
    
    if status == "booked":
        query = query.filter(
            Booking.status == "booked"
        )
    elif status == "completed":
        query = query.filter(
            Booking.status == "completed"
        )
    elif status == "cancelled":
        query = query.filter(
            Booking.status == "cancelled"
        )

    bookings = (
        query
        .order_by(Booking.booking_date.desc())
        .all()
    )

    return render_template(
        "admin/bookings.html",
        bookings=bookings,
        status=status,
        all_count=all_count,
        booked=booked,
        completed=completed,
        cancelled=cancelled,
        search=search
    )
