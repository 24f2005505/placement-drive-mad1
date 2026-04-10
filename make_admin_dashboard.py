
from model import User, db, Application, Student, Job, Company
from werkzeug.security import check_password_hash
from flask import render_template, request, flash, redirect
from flask_login import login_required, login_user, logout_user, current_user
from view import view
from restrict_access import restrict, all_restrict



def get_dashboard_stats():
    stats = {}
    stats['total_students'] = User.query.filter_by(role="student").count()
    stats['total_companies'] = User.query.filter_by(role="HR").count()
    stats['total_students_approved'] = User.query.filter_by(role="student", admin_approval_status="approved").count()
    stats['total_companies_approved'] = User.query.filter_by(role="HR", admin_approval_status="approved").count()
    stats['total_students_pending'] = User.query.filter_by(role="student", admin_approval_status="pending").count()
    stats['total_companies_pending'] = User.query.filter_by(role="HR", admin_approval_status="pending").count()
    stats['total_students_placed'] = Student.query.filter_by(placed=True).count()
    stats['total_drives'] = Job.query.count()
    stats['total_pending_drives'] = Job.query.filter_by(admin_approval_status="pending").count()
    return stats


############### seach functions ################
def search_for_students(query):
    users = User.query.filter(User.fname.ilike(f"%{query}%") | User.lname.ilike(f"%{query}") | User.email.ilike(f"%{query}")).all()
    user_ids = [user.id for user in users]

    students = Student.query.filter(Student.sid == query).all()
    user_ids += [student.sid for student in students]
    if not user_ids:
        flash("Query did not match any results.")
        return None
    return user_ids


def search_for_jobs(query):
    jobs = Job.query.filter(Job.job_title.ilike(f"%{query}%")).all()
    job_ids = [job.id for job in jobs]
    companies = Company.query.filter(Company.company_name.ilike(f"%{query}%")).all()
    company_ids = [company.id for company in companies]
    if company_ids:
        company_jobs = Job.query.filter(Job.company_id.in_(company_ids)).all()
        job_ids += [job.id for job in company_jobs]
    if not job_ids:
        flash("Query did not match any results.")
        return None
    return job_ids

def search_for_companies(query):
    companies = Company.query.filter(Company.company_name.ilike(f"%{query}%")).all()
    user_ids = [cs.company_hr_id for cs in companies]

    companies = Company.query.filter(Company.id == query).all()
    user_ids += [cs.company_hr_id for cs in companies]
    if not user_ids:
        flash("Query did not match any results.")
        return None
    return user_ids

def search_for_applications(query):
    users = User.query.filter(User.fname.ilike(f"%{query}%") | User.lname.ilike(f"%{query}")).all()
    students = [u.student for u in users if u.role == "student"]
    company_names = Company.query.filter(Company.company_name.ilike(f"%{query}%")).all()
    search_applications_ids =  [application.id for application in Application.query.filter(Application.id== query).all()]
    stu_id = [student.id for student in students]
    comp_id = [company.id for company in company_names]
    
    jobs = [Job.query.filter(Job.company_id == coid).first() for coid in comp_id]
    jobs_id = [job.id for job in jobs]

    ## built applications from above
    applications = Application.query.filter((Application.student_id.in_(stu_id) |  (Application.job_id.in_(jobs_id)) | Application.id.in_(search_applications_ids))).all()
    application_ids = [application.id for application in applications]
    if not application_ids:
        flash("Query did not match any results.")
        return None
    return application_ids
    



#################### make table functions ################

def make_table_from_students(user_ids= None):
    table_html = '''
    <table class = "table-striped table-bordered">
       <thead>
        <tr>
        <th class="px-3 py-2">Student Name</th>
        <th class="px-3 py-2">Student Email</th>
        <th class="px-3 py-2">Student University</th>
        <th class="px-3 py-2">Student Placed</th>
        <th class="px-3 py-2">View Full Profile</th>
        </tr>
        </thead>
        <tbody>
    '''
    ## get all (student) users
    if user_ids is not None:
        users = User.query.filter((User.role== "student") & (User.id.in_(user_ids))).all()
    else:
        users = User.query.filter_by(role="student").all()
    for user in users:
        student = Student.query.filter_by(sid=user.id).first()
        table_html+=f'''
        <tr>
            <td class="px-3 py-2">{user.fname} {user.lname}</td>
            <td class="px-3 py-2">{user.email}</td>
            <td class="px-3 py-2">{student.university}</td>
            <td class="px-3 py-2">{"Yes" if student.placed else "No"}</td>
            <td class = "px-2 py-2" ><form class = "m-0" action = "/admin/view" method = "GET"><input type ="hidden" name="user_id" value = "{user.id}"><button type = "submit" class = "btn btn-primary btn-sm">View</button></form></td>
        </tr>
        '''
    table_html+= '''
        </tbody>
        </table>
    '''
    return table_html

def make_table_from_company(user_ids= None):
    table_html = '''
    <table class = "table-striped table-bordered">
       <thead>
        <tr>
        <th class="px-3 py-2">Company Name</th>
        <th class="px-3 py-2">Company Type</th>
        <th class="px-3 py-2">HR Name</th>
        <th class="px-3 py-2">HR Contact</th>
        <th class="px-3 py-2">View Full Profile</th>
        </tr>
        </thead>
        <tbody>
    '''
    ## get all (student) users
    if user_ids is not None:
        users = User.query.filter((User.role== "HR") & (User.id.in_(user_ids))).all()
    else:
        users = User.query.filter_by(role="HR").all()
    for user in users:
        company = Company.query.filter_by(company_hr_id=user.id).first()
        table_html+=f'''
        <tr>
            <td class="px-3 py-2">{company.company_name}</td>
            <td class="px-3 py-2">{company.company_type}</td>
            <td class="px-3 py-2">{user.fname} {user.lname}</td>
            <td class="px-3 py-2">{user.email}</td>
            <td class = "px-2 py-2" ><form class = "m-0" action = "/admin/view" method = "GET"><input type ="hidden" name="user_id" value = "{user.id}"><button type = "submit" class = "btn btn-primary btn-sm">View</button></form></td>
        </tr>
        '''
    table_html+= '''
        </tbody>
        </table>
    '''
    return table_html


def make_table_from_jobs(job_ids=None):
    table_html = '''
    <table class="table-striped table-bordered">
       <thead>
        <tr>
        <th class="px-3 py-2">Job Title</th>
        <th class="px-3 py-2">Company Name</th>
        <th class="px-3 py-2">Salary Range</th>
        <th class="px-3 py-2">Total placed students</th>
        <th class="px-3 py-2">View Full Profile</th>
        </tr>
        </thead>
        <tbody>
    '''
    if job_ids is not None:
        jobs = Job.query.filter(Job.id.in_(job_ids)).all()
    else:
        jobs = Job.query.all()
    for job in jobs:
        company = Company.query.filter_by(id=job.company_id).first()
        company_name = company.company_name if company else "Not Available"
        applications = Application.query.filter_by(job_id=job.id).all()
        total_placed = len([api for api in applications if api.application_status == "accepted"])
        table_html += f'''
        <tr>
            <td class="px-3 py-2">{job.job_title}</td>
            <td class="px-3 py-2">{company_name}</td>
            <td class="px-3 py-2">{job.salary_range}</td>
            <td class="px-3 py-2">{total_placed}</td>
            <td class="px-2 py-2"><form class="m-0" action="/admin/view" method="GET"><input type="hidden" name="job_id" value="{job.id}"><button type="submit" class="btn btn-primary btn-sm">View</button>
            </form>
            </td>
        </tr>
        '''
    table_html += '''
        </tbody>
        </table>
    '''
    return table_html


def make_table_from_applications(application_ids = None):
    if application_ids:
        applications = Application.query.filter(Application.id.in_(application_ids)).all()
    else:
        applications = Application.query.all()
    
    table_html = '''
    <table class="table-striped table-bordered">
       <thead>
        <tr>
        <th class="px-3 py-2">Student Name</th>
        <th class="px-3 py-2">Company Name</th>
        <th class="px-3 py-2">Job Title</th>
        <th class="px-3 py-2">Status</th>
        <th class="px-3 py-2">View Full Profile</th>
        </tr>
        </thead>
        <tbody>
    '''
    for application in applications:
        student = Student.query.filter_by(id = application.student_id).first()
        user = student.user
        job = Job.query.filter(Job.id == application.job_id).first()
        company = job.company
        
        table_html += f'''
        <tr>
            <td class="px-3 py-2">{user.fname} {user.lname}</td>
            <td class="px-3 py-2">{company.company_name}</td>
            <td class="px-3 py-2">{job.job_title}</td>
            <td class="px-3 py-2">{application.application_status.capitalize()}</td>
            <td class="px-2 py-2"><form class="m-0" action="/admin/view" method="GET"><input type="hidden" name="application_id" value="{application.id}"><button type="submit" class="btn btn-primary btn-sm">View</button>
            </form> </td>

        </tr>
        '''
    table_html += '''
    </tbody>
    </table>
    '''
    return table_html   



################# main function ################
def make_dashboard(app):
    
    @app.route('/admin/dashboard')
    @all_restrict("admin")
    def admin_dashboard():
        return render_template('admin/dashboard.html', stats=get_dashboard_stats())    
    
    
    @app.route('/admin/student', methods = ["GET", "POST"])
    @restrict("admin")
    def admin_student():
        user_ids = None
        pending_users = User.query.filter((User.role== "student")  & (User.admin_approval_status == "pending")).all()
        pending_user_ids =  [pending_user.id for pending_user in pending_users]
        if request.method == "POST":
            query = request.form.get("query")
            user_ids = search_for_students(query)
            if not user_ids:
                pending_user_ids = []
            else: pending_user_ids = [pui for pui in pending_user_ids if pui in user_ids]
        
        return render_template('admin/student.html', student_table = make_table_from_students(user_ids), pending_student_table = make_table_from_students(pending_user_ids))
    
    @app.route('/admin/company', methods = ["GET", "POST"])
    @restrict("admin")
    def admin_company():
        user_ids = None
        pending_users = User.query.filter((User.role== "HR")  & (User.admin_approval_status == "pending")).all()
        pending_user_ids =  [pending_user.id for pending_user in pending_users]
        if request.method == "POST":
            query = request.form.get("query")
            user_ids = search_for_companies(query)
            pending_user_ids = [pui for pui in pending_user_ids if pui in user_ids]

        return render_template('admin/company.html', company_table = make_table_from_company(user_ids), pending_company_table = make_table_from_company(pending_user_ids))
    

    @app.route('/admin/job', methods=["GET", "POST"])
    @restrict("admin")
    def admin_job():
        pending_jobs = Job.query.filter((Job.admin_approval_status == "pending")).all()
        pending_job_ids =  [pending_job.id for pending_job in pending_jobs]
        job_ids = None
        if request.method == "POST":
            query = request.form.get("query")
            job_ids = search_for_jobs(query)
            pending_job_ids = [pji for pji in pending_job_ids if pji in job_ids]
        return render_template('admin/job.html', job_table=make_table_from_jobs(job_ids), pending_job_table=make_table_from_jobs(pending_job_ids))
    
    @app.route('/admin/applications', methods=["GET", "POST"])
    @restrict("admin")
    def admin_applications():
        application_ids = None
        if request.method == "POST":
            query = request.form.get("query")
            application_ids = search_for_applications(query)
        return render_template('admin/applications.html', app_table=make_table_from_applications(application_ids))

    ######################### View Functions ############################
    
    @app.route('/admin/view')
    @restrict("admin")
    def admin_view():
        try:
            user_id = request.args.get("user_id")
            view_obj = view(user_id, who_is_viewing="admin",job = False)
        except Exception as e:
            job_id = request.args.get("job_id")
            view_obj = view(job_id, who_is_viewing="admin",job= True)
        
        if request.args.get("application_id"):
            application_id = int(request.args.get("application_id"))
            view_obj = view(application_id, who_is_viewing="admin", application=True)

        return render_template('admin/view.html', user_string=view_obj.construct_view())
    
    @app.route('/admin/_approve', methods = ["POST"])
    @restrict("admin")
    def _approve():
        try:
            user_id_to_approve = request.form.get("user_id")
            user = User.query.filter_by(id=user_id_to_approve).first()
            view_obj = view(user.id, who_is_viewing="admin")
            user.admin_approval_status = "approved"
            db.session.commit()
        except:
            job_id_to_approve = request.form.get("job_id")
            job = Job.query.filter_by(id=job_id_to_approve).first()
            view_obj = view(job.id, job = True, who_is_viewing="admin")
            job.admin_approval_status = "approved"
            db.session.commit()
        
        return render_template('admin/view.html', user_string=view_obj.construct_view())
    
    @app.route('/admin/_not_approve', methods = ["POST"])
    @restrict("admin")
    def _not_approve():
        try:
            user_id_to_approve = request.form.get("user_id")
            user = User.query.filter_by(id=user_id_to_approve).first()
            view_obj = view(user.id, who_is_viewing="admin")
            user.admin_approval_status = "not-approved"
            db.session.commit()
        except:
            job_id_to_approve = request.form.get("job_id")
            job = Job.query.filter_by(id=job_id_to_approve).first()
            view_obj = view(job.id, job = True, who_is_viewing="admin")
            job.admin_approval_status = "not-approved"
            db.session.commit()
        return render_template('admin/view.html', user_string=view_obj.construct_view())
    
    @app.route('/admin/_ban', methods = ["POST"])
    @restrict("admin")
    def _ban():
        user_id_to_ban = request.form.get("user_id")
        user = User.query.filter_by(id=user_id_to_ban).first()
        view_obj = view(user.id, who_is_viewing="admin")
        user.admin_enforced_blacklist_status = True
        user.admin_approval_status = "not-approved" ## automatically set to not approved if banned
        db.session.commit()
        return render_template('admin/view.html', user_string=view_obj.construct_view())
    
    @app.route('/admin/_unban', methods = ["POST"])
    @restrict("admin")
    def _unban():
        user_id_to_ban = request.form.get("user_id")
        user = User.query.filter_by(id=user_id_to_ban).first()
        view_obj = view(user.id, who_is_viewing="admin")
        user.admin_enforced_blacklist_status = False
        db.session.commit()
        return render_template('admin/view.html', user_string=view_obj.construct_view())
    
    @app.route('/admin/edit_user', methods = ["GET"])
    @restrict("admin")
    def edit_user():
        user_id_to_edit = request.args.get("user_id")
        user = User.query.filter_by(id=user_id_to_edit).first()
        if user.role == "student":
            student = Student.query.filter_by(sid=user.id).first()
            return render_template('admin/student_profile.html', student= student)
        elif user.role == "HR":
            company = Company.query.filter_by(company_hr_id=user.id).first()
            return render_template('admin/company_profile.html', company = company)
        else:
            flash("User does not exist.")
            return render_template('admin/dashboard.html', stats=get_dashboard_stats())
    
    
    @restrict("admin")
    @app.route('/admin/_save_profile', methods = ["POST"])
    def _save_profile():
        user_id = request.form.get("user_id")
        view_obj = view(user_id, who_is_viewing="admin",job = False)
        user = User.query.filter_by(id=user_id).first()
        if request.method == "POST":
            if user.role == "HR":
                user.fname = request.form.get("fname")
                user.lname = request.form.get("lname")
                user.gender = request.form.get("gender")
                user.company.company_name = request.form.get("company_name")
                user.company.company_type = request.form.get("company_type")
                user.company.company_area = request.form.get("company_area")
                user.company.company_description = request.form.get("company_description")
                user.company.website_url = request.form.get("website_url")
                db.session.commit()
                flash("Sucessfully saved.")
            elif user.role == "student":
                import os
                from werkzeug.utils import secure_filename
                from flask import current_app
                user.fname = request.form.get("fname")
                user.lname = request.form.get("lname")
                user.gender = request.form.get("gender")
                resume = request.files.get("resume")
                if resume and resume.filename:
                    resume = request.files.get("resume")

                    filename = secure_filename(resume.filename)
                    filename_check = filename.lower().endswith(".pdf")
                    if not filename_check:
                        flash("Resume must be in PDF format.")
                        return render_template('student/profile.html')
                    filename = "Resume" + user.fname + "_" + user.lname + "_" + str(user.id) + ".pdf"
                    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                    resume.save(save_path)
                    resume_path = f"user_uploads/resumes/{filename}"
                else:
                    resume_path = user.student.resume_path
                user.gender = request.form.get("gender")
                user.student.university = request.form.get("university_name")
                user.student.major = request.form.get("major")
                user.student.gpa = request.form.get("gpa")
                user.student.resume_path = resume_path
                user.student.years_of_experience = request.form.get("exp")
                db.session.commit()
                flash("Sucessfully saved.")
            else:
                flash("Could not save.")
        return render_template('admin/view.html', user_string=view_obj.construct_view())