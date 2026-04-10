from functools import wraps
from flask import redirect, flash
from flask_login import current_user, login_required



def restrict(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect('/login')

            if current_user.admin_approval_status == "not-approved":
                flash("Your account is not approved, contact admin.")
                return redirect(f'/{role}/dashboard')

            if current_user.admin_approval_status != "approved":
                flash("Your account is not approved. Wait for admin approval.")
                return redirect(f'/{role}/dashboard')
            
            if role == "company": 
                expected_role = "HR"
            else:
                expected_role = role
            if current_user.role != expected_role:
                return redirect('/index')

            return f(*args, **kwargs)
        return wrapper
    return decorator

def all_restrict(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please login first.")
                return redirect('/login')

            if current_user.role != role:
                flash("Access denied.")
                return redirect('/index')
            return f(*args, **kwargs)
        return wrapper
    return decorator

