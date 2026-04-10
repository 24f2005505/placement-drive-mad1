from model import User, db, Application, Student, Job, Company
from flask import render_template, request, flash, redirect
from flask_login import login_required, current_user
from view import view
from datetime import date
from restrict_access import restrict, all_restrict


class Vars:
    def __init__(self, current_user):
        self.my_user = current_user
        self.my_student = current_user.student
        self.MY_APPLICATIONS = self.my_student.applications
        self.MY_APPLICATIONS_IDS = [application.id for application in self.MY_APPLICATIONS]
        self.applied_job_ids = []
        if self.MY_APPLICATIONS:
            self.applied_job_ids = [application.job_id for application in self.MY_APPLICATIONS]
        self.OPEN_JOBS = Job.query.filter((Job.admin_approval_status == "approved") & (Job.job_status == True) &(Job.deadline >= date.today()) & (~Job.id.in_(self.applied_job_ids))).all()
        self.OPEN_JOB_IDS = [job.id for job in self.OPEN_JOBS]
        if self.my_student.placed:
            self.success_application = Application.query.filter_by(student_id=self.my_student.id, application_status="accepted").first()
            self.my_job = self.success_application.job

def get_dashboard_stats(vars):
    stats = {}
    stats['my_name'] = vars.my_user.fname + " " + vars.my_user.lname
    stats["my_university"] = vars.my_student.university
    stats['total_open_drives'] = len(vars.OPEN_JOBS)
    stats['total_companies'] =User.query.filter_by(role="HR", admin_approval_status="approved").count() ## user should know about approbed companies only
    stats['total_applications_sent'] = Application.query.filter_by(student_id=vars.my_student.id).count()
    stats['my_approval'] = vars.my_user.admin_approval_status
    stats["is_shortlisted"] = "True" if Application.query.filter_by(student_id=vars.my_student.id, application_status="shortlisted").count() > 0 else "False"
    stats["is_offered"] = "True" if Application.query.filter_by(student_id=vars.my_student.id, application_status="offered").count() > 0 else "False"
    ## stats["is_accepted"] = "True" if Application.query.filter_by(student_id=vars.my_student.id, application_status="accepted").count() > 0 else "False"
    stats['is_placed'] = "True" if vars.my_student.placed else "False"
    if stats['is_placed'] == "True":
        stats["company_name"] = vars.my_job.company.company_name
        stats["job_title"] = vars.my_job.job_title
    return stats


############### seach functions ################
def search_open_jobs(query, OPEN_JOB_IDS, applied_job_ids): ## open + approved + not yet applied
    jobs = Job.query.filter((Job.job_title.ilike(f"%{query}%")) & (Job.id.in_(OPEN_JOB_IDS))).all()
    job_ids = [job.id for job in jobs]

    ## search by company name
    companies = Company.query.filter(Company.company_name.ilike(f"%{query}%")).all()
    company_ids = [company.id for company in companies]
    if company_ids:
        company_jobs = Job.query.filter((Job.company_id.in_(company_ids))  & (Job.id.in_(OPEN_JOB_IDS))).all()
        job_ids += [job.id for job in company_jobs if job.id not in applied_job_ids]
    job_ids = list(set(job_ids))
    if not job_ids:
        flash("Query did not match return any results.")
        return None
    return job_ids


def search_applied_jobs(query, applied_job_ids): ## only jobs student already applied to
    if not applied_job_ids:
        flash("No applied placement drives found.")
        return None

    jobs = Job.query.filter((Job.id.in_(applied_job_ids)) &(Job.job_title.ilike(f"%{query}%"))).all()
    job_ids = [job.id for job in jobs]

    companies = Company.query.filter(Company.company_name.ilike(f"%{query}%")).all()
    company_ids = [company.id for company in companies]
    if company_ids:
        company_jobs = Job.query.filter((Job.id.in_(applied_job_ids)) &(Job.company_id.in_(company_ids))).all()
        job_ids += [job.id for job in company_jobs]
    job_ids = list(set(job_ids))
    if not job_ids:
        flash("Query did not match any applied placement drives.")
        return None
    return job_ids



#################### make table functions ################

def make_table_from_open_jobs(OPEN_JOB_IDS, job_ids=None):
    table_html = '''
    <table class="table-striped table-bordered">
       <thead>
        <tr>
        <th class="px-3 py-2">Job Title</th>
        <th class="px-3 py-2">Company Name</th>
        <th class="px-3 py-2">Salary Range</th>
        <th class="px-3 py-2">Deadline</th>
        <th class="px-3 py-2">View Full</th>
        </tr>
        </thead>
        <tbody>
    '''

    if job_ids:
        jobs = Job.query.filter(Job.id.in_(job_ids)).all()
    else:
        jobs = Job.query.filter(Job.id.in_(OPEN_JOB_IDS)).all()

    for job in jobs:
        table_html += f'''
        <tr>
            <td class="px-3 py-2">{job.job_title}</td>
            <td class="px-3 py-2">{job.company.company_name}</td>
            <td class="px-3 py-2">{job.salary_range}</td>
            <td class="px-3 py-2">{job.deadline}</td>
            <td class="px-2 py-2">
                <form class="m-0" action="/student/view" method="GET"><input type="hidden" name="job_id" value="{job.id}"><button type="submit" class="btn btn-primary btn-sm">View</button>
                </form>
            </td>
        </tr>
        '''
    table_html += '''
        </tbody>
        </table>
    '''
    return table_html


def make_table_from_applied_jobs(my_student, applied_job_ids, job_ids=None ):
    table_html = '''
    <table class="table-striped table-bordered">
       <thead>
        <tr>
        <th class="px-3 py-2">Job Title</th>
        <th class="px-3 py-2">Company Name</th>
        <th class="px-3 py-2">Salary Range</th>
        <th class="px-3 py-2">Application Status</th>
        <th class="px-3 py-2">View Full Profile</th>
        </tr>
        </thead>
        <tbody>
    '''

    if job_ids:
        jobs = Job.query.filter(Job.id.in_(job_ids)).all()
    else:
        jobs = Job.query.filter(Job.id.in_(applied_job_ids)).all() if applied_job_ids else []

    for job in jobs: ## each job should have only one application
        application = Application.query.filter_by(job_id=job.id, student_id=my_student.id).first()
        application_status = application.application_status.capitalize()

        table_html += f'''
        <tr>
            <td class="px-3 py-2">{job.job_title}</td>
            <td class="px-3 py-2">{job.company.company_name}</td>
            <td class="px-3 py-2">{job.salary_range}</td>
            <td class="px-3 py-2">{application_status}</td>
            <td class="px-2 py-2">
                <form class="m-0" action="/student/view" method="GET"><input type="hidden" name="application_id" value="{application.id}"><button type="submit" class="btn btn-primary btn-sm">View</button>
                </form>
            </td>
        </tr>
        '''

    table_html += '''
        </tbody>
        </table>
    '''
    return table_html




################# main function ################
def make_dashboard(app):

    @app.route('/student/dashboard')
    @all_restrict("student")
    def student_dashboard():
        vars = Vars(current_user)
        return render_template('student/dashboard.html', stats=get_dashboard_stats(vars))    
    
    @app.route('/student/placement_drives', methods=["GET", "POST"])
    @restrict(role="student")
    def student_placement_drives():
        vars = Vars(current_user)
        job_ids = None
        if request.method == "POST":
            query = request.form.get("query")
            job_ids = search_open_jobs(query, vars.OPEN_JOB_IDS, vars.applied_job_ids)

        return render_template(
            'student/placement_drives.html', job_table=make_table_from_open_jobs(OPEN_JOB_IDS=vars.OPEN_JOB_IDS, job_ids=job_ids)
        )

    @app.route('/student/view')
    @restrict("student")
    def student_view():
        vars = Vars(current_user)
        if request.args.get("job_id"):
            job_id = int(request.args.get("job_id"))
            view_obj = view(job_id, who_is_viewing="student", job=True)
            if job_id not in vars.OPEN_JOB_IDS:
                flash("Access denied.")
                return redirect('/student/placement_drives')

        if request.args.get("application_id"):
            application_id = int(request.args.get("application_id"))
            view_obj = view(application_id, who_is_viewing="student", application=True)
            if application_id not in vars.MY_APPLICATIONS_IDS:
                flash("Access denied.")
                return redirect('/student/placement_drives')

        return render_template('student/view.html', user_string=view_obj.construct_view())
    
    @app.route('/student/profile', methods=["GET", "POST"])
    @restrict("student")
    def student_profile():
        if request.method == "POST":
            import os
            from flask import current_app
            from werkzeug.utils import secure_filename

            current_user.fname = request.form.get("fname")
            current_user.lname = request.form.get("lname")
            resume = request.files.get("resume")
            if resume and resume.filename:
                resume = request.files.get("resume")

                filename = secure_filename(resume.filename)
                filename_check = filename.lower().endswith(".pdf")
                if not filename_check:
                    flash("Resume must be in PDF format.")
                    return render_template('student/profile.html')
                filename = "Resume" + current_user.fname + "_" + current_user.lname + "_" + str(current_user.id) + ".pdf"
                save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                resume.save(save_path)
                resume_path = f"user_uploads/resumes/{filename}"
            else:
                resume_path = current_user.student.resume_path

            
            current_user.gender = request.form.get("gender")
            current_user.student.university = request.form.get("university_name")
            current_user.student.major = request.form.get("major")
            current_user.student.gpa = request.form.get("gpa")
            current_user.student.resume_path = resume_path
            current_user.student.years_of_experience = request.form.get("exp")
            db.session.commit()
            flash("Sucessfully saved.")
        return render_template('student/profile.html')
    

    @app.route('/student/history', methods = ["GET", "POST"])
    @restrict("student")
    def student_history():
        
        vars = Vars(current_user)
        return render_template('student/history.html', stats = get_dashboard_stats(vars), make_table_from_applied_jobs=make_table_from_applied_jobs(vars.my_student, vars.applied_job_ids))
    
    @app.route('/student/_to_application_form', methods=["GET", "POST"])
    @restrict("student")
    def _to_application_form():
        from datetime import date
        current_date = date.today()
        vars = Vars(current_user)
        if vars.my_student.placed:
            flash("You have already been placed.")
            return redirect('/student/dashboard')
        job_id = request.form.get("job_id") 
        job = Job.query.filter_by(id=job_id).first()
        if job_id in vars.applied_job_ids:
            flash("You cannot apply again, you have already applied for this job.")
            return redirect('/student/dashboard')
        return render_template('student/application_form.html', job=job, user= current_user, date= current_date)

    @app.route('/student/_apply', methods=["POST"])
    @restrict("student")

    def _apply():
        from datetime import date
        vars = Vars(current_user)

        if vars.my_student.placed:
            flash("You have already been placed.")
            return redirect('/student/dashboard')

        job_id = int(request.form.get("job_id"))
        job = Job.query.filter_by(id=job_id).first()


        if job_id not in vars.OPEN_JOB_IDS:
            flash("Access denied.")
            return redirect('/student/placement_drives')

        if job_id in vars.applied_job_ids:
            flash("You have already applied for this job.")
            return redirect('/student/placement_drives')

        application = Application(
            student_id=vars.my_student.id,
            job_id=job_id,
            application_status="pending",
            cover_letter=request.form.get("cover_letter"),
            relevant_skills=request.form.get("relevant_skills"),
            date = date.today()
        )

        db.session.add(application)
        db.session.commit()

        flash("Application submitted successfully.")
        return redirect('/student/placement_drives')
    

    @app.route('/student/_withdraw', methods=["POST"])
    @restrict("student")
    def _withdraw():
        vars = Vars(current_user)
        application_id = int(request.form.get("application_id"))
        if application_id not in vars.MY_APPLICATIONS_IDS:
            flash("Access denied.")
            return redirect('/student/history')

        application = Application.query.filter_by(id=application_id).first()

        if application.application_status == "accepted":
            flash("You cannot withdraw this application.")
            return redirect('/student/history')

        application.application_status = "withdrawn"
        db.session.commit()
        flash("Application withdrawn successfully.")
        return redirect('/student/history')
    

    @app.route('/student/_accept_offer', methods=["POST"])
    @restrict("student")
    def _accept_offer():
        vars = Vars(current_user)
        application_id = int(request.form.get("application_id"))
        if application_id not in vars.MY_APPLICATIONS_IDS:
            flash("Access denied.")
            return redirect('/student/history')
        application = Application.query.filter_by(id=application_id).first()
        if application.application_status != "offered":
            flash(f"This application is {application.application_status}.")
            return redirect('/student/history')
        current_user.student.placed = True
        application.application_status = "accepted"
        my_applications = [Application.query.filter_by(id=id).first() for id in vars.MY_APPLICATIONS_IDS]
        for application in my_applications:
            if application.application_status in ["pending", "offered", "shortlisted"]:
                application.application_status = "withdrawn"
        db.session.commit()
        flash("Offer accepted successfully.")
        return redirect('/student/dashboard')
