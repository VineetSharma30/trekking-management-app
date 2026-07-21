from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from .utils import redirect_dashboard

user_bp = Blueprint("user", __name__)

@user_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "user" :
        return render_template("user/dashboard.html")
    
    flash("Access denied.", "danger")
    return redirect_dashboard(current_user)
