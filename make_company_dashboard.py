from model import User, db, Application, Student, Job, Company
from flask import render_template, request, flash, redirect
from flask_login import login_required, current_user
from view import view
from datetime import date
from restrict_access import restrict, all_restrict


class Vars:
    def __init__(self, current_user):
        self.my_user = current_user
        self.my_company = current_user.company
        self.MY_ALL_JOBS = Job.query.filter_by(company_id=self.my_company.id).all()
        self.MY_ALL_JOB_IDS = [job.id for job in self.MY_ALL_JOBS]
        self.OPEN_JOBS = Job.query.filter((Job.company_id == self.my_company.id) &(Job.job_status == True) & (Job.deadline >= date.today())).all()
        self.OPEN_JOB_IDS = [job.id for job in self.OPEN_JOBS]
        self.MY_ALL_APPLICATIONS_ID = [application.id for application in Application.query.filter(Application.job_id.in_(self.MY_ALL_JOB_IDS)).all()]


##################### dashboard content ###########################
def get_dashboard_stats(vars):
    stats = {}
    stats['my_name'] = vars.my_user.fname + " " + vars.my_user.lname
    stats["company_name"] = vars.my_company.company_name
    stats['total_open_drives'] = len(vars.OPEN_JOBS)
    stats['total_drives'] = len(vars.MY_ALL_JOBS)
    stats['total_applications'] = Application.query.filter(Application.job_id.in_(vars.MY_ALL_JOB_IDS)).count()
    stats["total_pending_applications"] = Application.query.filter((Application.job_id.in_(vars.MY_ALL_JOB_IDS)) & (Application.application_status == "pending")).count()
    stats['total_students_hired'] = Student.query.join(Application).join(Job).filter((Job.company_id == vars.my_company.id) & (Application.application_status == "accepted")).count()
    stats['my_approval'] = vars.my_user.admin_approval_status
    return stats




################################## make tables content ####################
def make_table_from_my_jobs(MY_JOB_IDS):
    table_html = '''
    <table class="table-striped table-bordered">
       <thead>
        <tr>
        <th class="px-3 py-2">Job Title</th>
        <th class="px-3 py-2">Salary Range</th>
        <th class="px-3 py-2">Deadline</th>
        <th class="px-3 py-2">Status</th>
        <th class="px-3 py-2">View Details</th>
        <th class="px-3 py-2">View Applicants</th>
        </tr>
        </thead>
        <tbody>
    '''

    jobs = Job.query.filter(Job.id.in_(MY_JOB_IDS)).all()

    for job in jobs:
        table_html += f'''
        <tr>
            <td class="px-3 py-2">{job.job_title}</td>
            <td class="px-3 py-2">{job.salary_range}</td>
            <td class="px-3 py-2">{job.deadline}</td>
            <td class="px-3 py-2">{"Open" if job.job_status else "Closed"}</td>
            <td class="px-2 py-2">
                <form class="m-0" action="/company/view" method="POST"><input type="hidden" name="job_id" value="{job.id}"><button type="submit" class="btn btn-primary btn-sm">View</button>
                </form>
            </td>
            <td class="px-2 py-2">
                <form class="m-0" action="/company/placement_drives" method="GET"><input type="hidden" name="job_id" value="{job.id}"><button type="submit" class="btn btn-primary btn-sm">View</button>
                </form>
            </td>
        </tr>
        '''
    table_html += '''
        </tbody>
        </table>
    '''
    return table_html


def make_table_from_applicants(job_id):
    table_html = '''
    <table class="table-striped table-bordered">
       <thead>
        <tr>
        <th class="px-3 py-2">Student Name</th>
        <th class="px-3 py-2">University</th>
        <th class="px-3 py-2">Major</th>
        <th class="px-3 py-2">GPA</th>
        <th class="px-3 py-2">Application Status</th>
        <th class="px-3 py-2">View Application</th>
        </tr>
        </thead>
        <tbody>
    '''

    applications = Application.query.filter_by(job_id=job_id).all()

    for application in applications:
        student = application.student
        user = student.user
        application_status = application.application_status 

        table_html += f'''
        <tr>
            <td class="px-3 py-2">{user.fname} {user.lname}</td>
            <td class="px-3 py-2">{student.university}</td>
            <td class="px-3 py-2">{student.major}</td>
            <td class="px-3 py-2">{student.gpa}</td>
            <td class="px-3 py-2">{application_status.capitalize()}</td>
            <td class="px-2 py-2">
                <form class="m-0" action="/company/view" method="GET"><input type="hidden" name="application_id" value="{application.id}"><button type="submit" class="btn btn-primary btn-sm">View</button>
                </form>
            </td>
        </tr>
        '''
    table_html += '''
        </tbody>
        </table>
    '''
    return table_html



################################## actual routes ############################3
import datetime
def make_dashboard(app):

    @app.route('/company/dashboard')
    @all_restrict("HR")
    def company_dashboard():
        vars = Vars(current_user)
        return render_template('company/dashboard.html', stats=get_dashboard_stats(vars))
    

    @app.route('/company/profile', methods=["GET", "POST"])
    @restrict("company")
    def company_profile():
        if request.method == "POST":
            current_user.fname = request.form.get("fname")
            current_user.lname = request.form.get("lname")
            current_user.gender = request.form.get("gender")
            current_user.company.company_name = request.form.get("company_name")
            current_user.company.company_type = request.form.get("company_type")
            current_user.company.company_area = request.form.get("company_area")
            current_user.company.company_description = request.form.get("company_description")
            current_user.company.website_url = request.form.get("website_url")
            db.session.commit()
            flash("Sucessfully saved.")
        return render_template('company/profile.html')


    @app.route('/company/new_drive', methods=["GET", "POST"])
    @restrict("company")
    def new_drive():
        from datetime import datetime
        if request.method == "POST":
            data_str = (request.form.get("deadline"))
            min_req_gpa = request.form.get("min_req_gpa")
            try:
                min_req_gpa = float(min_req_gpa)
            except ValueError:
                flash("Minimum GPA must be a number.")
                return redirect("/company/new_drive")
            job = Job(
                company_id=current_user.company.id,
                job_title=request.form.get("job_title"),
                job_description=request.form.get("job_description"),
                minimum_skills=request.form.get("minimum_skills"),
                location=request.form.get("location"),
                salary_range=request.form.get("salary_range"),
                deadline=datetime.strptime(data_str, "%Y-%m-%d").date(),
                min_req_gpa=float(request.form.get("min_req_gpa")),
                admin_approval_status="pending",
                job_status = True,
            )
            db.session.add(job)
            db.session.commit()
            flash("Placement drive created successfully.")
            return redirect('/company/placement_drives')

        return render_template('company/new_drive.html')


    @app.route('/company/placement_drives', methods=["GET", "POST"])
    @restrict("company")
    def placement_drives():
        vars = Vars(current_user)
        job_id = request.args.get("job_id")
        application_id = request.args.get("application_id")
        application_table = None

        if job_id:
            job_id = int(job_id)
            if job_id not in vars.MY_ALL_JOB_IDS:
                flash("Access denied.")
                return redirect('/company/placement_drives')
            application_table = make_table_from_applicants(job_id)

        return render_template('company/placement_drives.html', make_table_from_my_jobs=make_table_from_my_jobs(vars.MY_ALL_JOB_IDS),application_table=application_table)
    
    @app.route('/company/view', methods=["GET", "POST"])
    @restrict("company")
    def company_view():
        vars = Vars(current_user)

        if request.method == "POST":
            job_id = int(request.form.get("job_id"))
            if job_id not in vars.MY_ALL_JOB_IDS:
                flash("Access denied.")
                return redirect('/company/placement_drives')
            view_obj = view(job_id, who_is_viewing="company", job=True)
            return render_template('company/view.html', user_string=view_obj.construct_view())

        application_id = int(request.args.get("application_id"))
        if application_id not in vars.MY_ALL_APPLICATIONS_ID:
            flash("Access denied.")
            return redirect('/company/placement_drives')
        view_obj = view(application_id, who_is_viewing="company", application=True)
        return render_template('company/view.html', user_string=view_obj.construct_view())

        
    @app.route('/company/_accept_', methods=["POST"])
    @restrict("company")
    def _accept_():
        vars = Vars(current_user)
        application_id = int(request.form.get("application_id"))
        if application_id not in vars.MY_ALL_APPLICATIONS_ID:
            flash("Access denied.")
            return redirect('/company/placement_drives')
        application = Application.query.filter_by(id=application_id).first()
        if application.application_status not in ["withdrawn", "accepted"]:
            application.application_status = "offered"
        db.session.commit()
        view_obj = view(application_id, who_is_viewing="company", application=True)
        return render_template('company/view.html', user_string=view_obj.construct_view())
    
    @app.route('/company/_reject_', methods=["POST"])
    @restrict("company")
    def _reject_():
        vars = Vars(current_user)
        application_id = int(request.form.get("application_id"))
        if application_id not in vars.MY_ALL_APPLICATIONS_ID:
            flash("Access denied.")
            return redirect('/company/placement_drives')
        application = Application.query.filter_by(id=application_id).first()
        if application.application_status not in ["withdrawn", "accepted"]:
            application.application_status = "rejected"
        db.session.commit()
        view_obj = view(application_id, who_is_viewing="company", application=True)
        return render_template('company/view.html', user_string=view_obj.construct_view())
    

    @app.route('/company/_shortlist_', methods=["POST"])
    @restrict("company")
    def _shortlist_():
        vars = Vars(current_user)
        application_id = int(request.form.get("application_id"))
        if application_id not in vars.MY_ALL_APPLICATIONS_ID:
            flash("Access denied.")
            return redirect('/company/placement_drives')
        application = Application.query.filter_by(id=application_id).first()
        if application.application_status not in ["withdrawn", "accepted"]:
            if application.application_status not in ["withdrawn", "accepted"]:
                application.application_status = "shortlisted"
        db.session.commit()
        view_obj = view(application_id, who_is_viewing="company", application=True)
        return render_template('company/view.html', user_string=view_obj.construct_view())

    @app.route('/company/_open_drive', methods=["POST"])
    @restrict("company")
    def _open_drive():
        vars = Vars(current_user)
        job_id = int(request.form.get("job_id"))
        if job_id not in vars.MY_ALL_JOB_IDS:
            flash("Access denied.")
            return redirect('/company/placement_drives')

        job = Job.query.filter_by(id=job_id).first()
        job.job_status = True
        db.session.commit()

        view_obj = view(job_id, who_is_viewing="company", job=True)
        return render_template('company/view.html', user_string=view_obj.construct_view())
    

    @app.route('/company/_close_drive', methods=["POST"])
    @restrict("company")
    def _close_drive():
        vars = Vars(current_user)
        job_id = int(request.form.get("job_id"))
        if job_id not in vars.MY_ALL_JOB_IDS:
            flash("Access denied.")
            return redirect('/company/placement_drives')

        job = Job.query.filter_by(id=job_id).first()
        applications = Application.query.filter_by(job_id=job_id).all()
        for application in applications:
            if application.application_status in ["pending"]:
                application.application_status = "rejected"
        job.job_status = False
        db.session.commit()

        view_obj = view(job_id, who_is_viewing="company", job=True)
        return render_template('company/view.html', user_string=view_obj.construct_view())
    
    
    @app.route("/company/edit_drive", methods=["GET", "POST"])
    @restrict("company")
    def edit_drive():
        
        if request.method == "GET":
            job_id = request.args.get("job_id")
            job_id = int(job_id)
        else:
            job_id = request.form.get("job_id")
            job_id = int(job_id)

        vars = Vars(current_user)
        
        view_obj = view(job_id, who_is_viewing="company", job=True)
        if job_id not in vars.MY_ALL_JOB_IDS:
                flash("Access denied.")
                return redirect('/company/placement_drives')
        else:
            job = Job.query.get(job_id)
        
           
        if request.method == "POST":
            from datetime import datetime
            ## actual edits
            min_req_gpa = request.form.get("min_req_gpa")
            try:
                min_req_gpa = float(min_req_gpa)
            except ValueError:
                flash("Minimum GPA must be a number.")
                return redirect(f"/company/edit_drive?job_id={job_id}")
            date_str = request.form.get("deadline")

            try:
                min_req_gpa = float(min_req_gpa)
            except ValueError:
                flash("Minimum GPA must be a number.")
                return redirect(f"/company/edit_drive?job_id={job_id}")


            job.job_title = request.form.get("job_title")
            job.job_description = request.form.get("job_description")
            job.minimum_skills = request.form.get("minimum_skills")
            job.location = request.form.get("location")
            job.salary_range = request.form.get("salary_range")
            job.deadline = datetime.strptime(date_str, "%Y-%m-%d").date()
            job.min_req_gpa = min_req_gpa
            job.admin_approval_status = "pending"
            db.session.commit()
            
            flash("Sucessfully saved.")
            return render_template("company/view.html", user_string=view_obj.construct_view())
        return render_template("company/edit_drive.html", job=job)