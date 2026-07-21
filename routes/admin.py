from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from .utils import redirect_dashboard

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin" :
        return render_template("admin/dashboard.html")
    
    flash("Access denied.", "danger")
    return redirect_dashboard(current_user)
    
