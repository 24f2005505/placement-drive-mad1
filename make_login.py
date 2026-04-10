from model import User
from werkzeug.security import check_password_hash
from flask import render_template, request, flash, redirect
from flask_login import login_required, login_user, logout_user, current_user


def make_login(app):
    @app.route('/login', methods = ["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            pwd_hash = request.form.get("password")
            user = User.query.filter_by(username = username).first()
            if user and check_password_hash(user.pwd_hash, pwd_hash) and not user.admin_enforced_blacklist_status:
                role = user.role
                login_user(user) ## log in the user

                flash("Login successful!")
                if role == "admin":
                    return redirect('/admin/dashboard')
                elif role == "student":
                    return redirect('/student/dashboard')
                elif role == "HR":
                    return redirect('/company/dashboard')
                else:
                    flash("Invalid user role. Please contact support.")
                    return redirect('/index')
            else:
                flash("Invalid username or password. Please try again.")
                return render_template('login.html')
        return render_template('login.html')


    @app.route('/logout')
    @login_required
    def logout():
        logout_user() ## log out the user
        flash("Logged out successfully!")
        return redirect('/index')



