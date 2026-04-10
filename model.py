from flask_sqlalchemy import SQLAlchemy as SA
from flask_login import UserMixin

db = SA()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False) ## admin, student, HR
    fname = db.Column(db.String(80), nullable=False)
    lname = db.Column(db.String(80), nullable=False)
    pwd_hash = db.Column(db.String(200), nullable=False)  ## hashed password
    gender =db.Column(db.String(40), nullable=False)  
    admin_approval_status = db.Column(db.String(20), default="pending", nullable=False)  ## pending, approved, not-approved 
    admin_enforced_blacklist_status = db.Column(db.Boolean, default=False, nullable=False)  ## if true, user is banned by admin and cannot log in 
    admin = db.relationship('Admin', back_populates='user', uselist=False)
    student = db.relationship('Student', back_populates='user', uselist=False)
    company = db.relationship('Company', back_populates='hr_user', uselist=False)
    company_contacts = db.relationship('company_contact', back_populates='hr_user')
    
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aid = db.Column(db.Integer, db.ForeignKey('user.id'))  ## admin id
    status = True
    user = db.relationship('User', back_populates='admin')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Integer, db.ForeignKey('user.id'))  ## student id
    placed = db.Column(db.Boolean, default=False, nullable=False)  ## yes, no
    major = db.Column(db.String(20), nullable=False)
    university = db.Column(db.String(80), nullable=False)
    gpa = db.Column(db.String(20), nullable=False)
    years_of_experience = db.Column(db.String(20), nullable=False)  ## 0 if no work experience
    resume_path = db.Column(db.String(200), nullable=False)  ## path to the resume file
    accepted_job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=True)  ## the job for which the student got accepted (null if not accepted for any job yet)
    user = db.relationship('User', back_populates='student')
    accepted_job = db.relationship('Job', foreign_keys=[accepted_job_id], back_populates='placed_students')
    applications = db.relationship('Application', back_populates='student')

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_hr_id = db.Column(db.Integer, db.ForeignKey('user.id'))  ## HR user id
    company_name = db.Column(db.String(80), nullable=False)
    company_type = db.Column(db.String(20), nullable=False)  ## startup, mid-size, large
    company_area = db.Column(db.String(80), nullable=False)  ## area of operation (e.g., tech, finance, healthcare)
    company_description = db.Column(db.String(500), nullable=False)  ## brief description of the company
    website_url = db.Column(db.String(200), nullable=True)  ## optional field for the company's website URL
    hr_user = db.relationship('User', back_populates='company')
    contacts = db.relationship('company_contact', back_populates='company')
    jobs = db.relationship('Job', back_populates='company')


class company_contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)  
    hr_user = db.relationship('User', back_populates='company_contacts')
    company = db.relationship('Company', back_populates='contacts')

class Job(db.Model): ## the placement drive
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_title = db.Column(db.String(80), nullable=False)
    job_description = db.Column(db.String(500), nullable=False)
    minimum_skills = db.Column(db.String(200), nullable=False)   ## eligiblity criteria
    location = db.Column(db.String(80), nullable=False)
    salary_range = db.Column(db.String(50), nullable=False)  
    job_status = db.Column(db.Boolean, nullable=False)  ## open, closed
    deadline = db.Column(db.Date, nullable=False)  ## application deadline
    min_req_gpa = db.Column(db.Float, nullable=False) 
    admin_approval_status = db.Column(db.String(20), default="pending", nullable=False)  ## pending, approved, not-approved 
    company = db.relationship('Company', back_populates='jobs')
    applications = db.relationship('Application', back_populates='job')
    placed_students = db.relationship('Student', foreign_keys='Student.accepted_job_id', back_populates='accepted_job')


class Application(db.Model): ## filled by the student when applying for a job
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    application_status = db.Column(db.String(20), nullable=False)  ## pending, shortlisted, offered, rejected, withdrawn, accepted
    cover_letter = db.Column(db.String(500), nullable=False)
    relevant_skills = db.Column(db.String(200), nullable=False)  ## comma-separated list of relevant skills for the job
    student = db.relationship('Student', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')
    date = db.Column(db.Date, nullable=False)