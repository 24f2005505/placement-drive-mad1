from model import db, User, Company, company_contact, Student
from werkzeug.security import generate_password_hash as ph
from flask import render_template, request, flash, redirect
import os
from werkzeug.utils import secure_filename
from flask import current_app

def username_unique(User, uname):
    bool_ = User.query.filter_by(username = uname).first() is None
    return bool_

def email_unique(User, email):
    bool_ = User.query.filter_by(email = email).first() is None
    return bool_

def make_form(app):
    
    @app.route('/register_student', methods = ["GET", "POST"])
    def register_student():
        ## handle unique username heere
        if request.method == "POST":
            if not username_unique(User, request.form["username"]):
                flash("Username already taken, please choose another one.")
                return render_template('register_stu.html')
            elif not email_unique(User, request.form["email"]):
                flash("This email is registered. Try logging in instead.")
                return render_template('register_stu.html')
            elif request.form["password"] != request.form["con_password"]:
                flash("Passwords do not match, please re-enter.")
                return render_template('register_stu.html')
            else:
                user = User(
                        username= request.form["username"],
                        email= request.form["email"],
                        role = "student",
                        fname = request.form["fname"],
                        lname = request.form["lname"],
                        pwd_hash = ph(request.form["password"]),  
                        gender = request.form["gender"]
                    )
                
                db.session.add(user)
                db.session.flush()
                
                resume = request.files.get("resume")
                if not resume or resume.filename == "":
                    flash("Resume is required.")
                    return render_template('register_stu.html')

                filename = secure_filename(resume.filename)
                filename_check = filename.lower().endswith(".pdf")
                if not filename_check:
                    flash("Resume must be in PDF format.")
                    return render_template('register_stu.html')
                filename = "Resume" + user.fname + "_" + user.lname + "_" + str(user.id) + ".pdf"
                save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                resume.save(save_path)
                resume_path = f"user_uploads/resumes/{filename}"

                student = Student(
                    major = request.form["major"],
                    sid = user.id,
                    university = request.form["university_name"],
                    gpa = request.form["gpa"],
                    resume_path = resume_path,
                    years_of_experience = request.form["exp"],
                    placed = False
                )   

         

                db.session.add(student)   
                db.session.commit()
        
            flash('Registration successful!')
            return redirect('/index')
        return render_template('register_stu.html')


    @app.route('/register_hr', methods = ["GET", "POST"])
    def register_hr():
        if request.method == "POST":
            if not username_unique(User, request.form["username"]):
                flash("Username already taken, please choose another one.")
                return render_template('register_hr.html')
            elif not email_unique(User, request.form["email"]):
                flash("This email is registered. Try logging in instead.")
                return render_template('register_hr.html')
            elif request.form["password"] != request.form["con_password"]:
                flash("Passwords do not match, please re-enter.")
                return render_template('register_hr.html')
            else:
                user = User(
                        username= request.form["username"],
                        email= request.form["email"],
                        role = "HR",
                        fname = request.form["fname"],
                        lname = request.form["lname"],
                        pwd_hash = ph(request.form["password"]),  
                        gender = request.form["gender"]
                    )
                db.session.add(user)
                db.session.commit()

                comp = Company(
                    company_hr_id = user.id,
                    company_name = request.form["comp_name"],
                    company_type = request.form["comp_type"],
                    company_area = request.form["comp_area"],
                    company_description = request.form["comp_desc"],
                    website_url = request.form["comp_website"]

                )
                db.session.add(comp)
                db.session.commit()

                comp_contact = company_contact(
                    hr_id = user.id,
                    company_id = comp.id
                )

                db.session.add(comp_contact)
                db.session.commit()
            flash('Registration successful!')
            return redirect('/index')
        return render_template('register_hr.html')