from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, StaffProfile
from .utils import redirect_dashboard

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated: 
        return redirect_dashboard(current_user)

    if request.method == "POST":

        username = request.form["username"].strip().lower()
        password = request.form["password"]
        remember = "remember" in request.form

        user = User.query.filter_by(username=username).first()

        # User doesn't exists
        if not user:
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html")
        
        # Ensure password is correct
        if not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html")
        
        # Ensure blacklisted users cannot login
        if user.status == "blacklisted":
            flash("Your account has been blocked.", "danger")
            return render_template("auth/login.html")
        
        # Staff should wait for approval before login
        if user.role == "staff" and user.staff_profile.approval_status != "approved" :
            flash("Your account is awaiting admin approval", "warning")
            return render_template("auth/login.html")
        
        # Everything is valid
        login_user(user, remember=remember)

        # Redirect users to their resp. dashboard
        return redirect_dashboard(user)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated: 
        return redirect_dashboard(current_user)
    
    if request.method == "POST":

        full_name = request.form["full_name"].strip()
        username = request.form["username"].strip().lower()
        email = request.form["email"].strip().lower()
        phone = request.form["phone"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]

        # Ensure pass and confirm pass both are same and valid
        if password != confirm_password or len(password) > 6 :
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")
        
        # Check if username is uniquw
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "danger")
            return render_template("auth/register.html")
        
        # Check if email is not already taken
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered.", "danger")
            return render_template("auth/register.html")
        
        # Ensure full name is valid
        if not full_name:
            flash("Full name is required.", "danger")
            return render_template("auth/register.html")

        # Prevent admin role creation
        if role not in ("user", "staff"):
            flash("Invalid role.", "danger")
            return render_template("auth/register.html")

        # Finally create user object
        new_user = User(
            username = username,
            email = email,
            password_hash = generate_password_hash(password),
            full_name = full_name,
            phone = phone,
            role = role,
        )

        try : 
            # Add user to db session
            db.session.add(new_user)

            # Check for staff role 
            if role == "staff":
                staff = StaffProfile(
                    user = new_user,
                    experience = 0
                )
                db.session.add(staff)

            # Commit user to db
            db.session.commit()

            if role == "staff" :
                flash("Registration successful. Wait for admin approval.", "success")
            else : 
                flash("Registration successful. Please login.", "success")

            return redirect(url_for("auth.login"))
        
        except Exception as e :
            
            # User registration failed rollback to current transaction
            db.session.rollback()
            print(e)
            flash("Something went wrong.", "danger")
            return render_template("auth/register.html")

    return render_template("auth/register.html")
