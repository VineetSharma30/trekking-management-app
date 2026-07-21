from flask import redirect, url_for, flash
from flask_login import logout_user

def redirect_dashboard(user) :
    if user.role == "admin" :
        return redirect(url_for("admin.dashboard"))
    elif user.role == "staff" :
        return redirect(url_for("staff.dashboard"))
    elif user.role == "user" :
        return redirect(url_for("user.dashboard"))
    
    # Logout users with invalid roles
    flash("Invalid user role", "danger")
    logout_user()
    return redirect(url_for("auth.login"))
