from model import User, Student, Application, Company, Job
class view():
    def __init__(self, user_id, who_is_viewing, job = False, application = False):
        self.who_is_viewing = who_is_viewing
        self.is_job = job
        self.is_application = application
        if not job and not application:
            self.user = User.query.filter_by(id=user_id).first()
            self.role = self.user.role
            self.user_id = user_id
        elif application:
            self.application = Application.query.filter_by(id=user_id).first() ## user_id here is the application id
            self.application_id = user_id
            self.student = self.application.student 
            self.student_user = self.student.user
            ## also want the job view
            self.job = self.application.job 
            self.job_id = self.job.id
        elif job:
            self.job = Job.query.filter_by(id=user_id).first()
            self.job_id = user_id
        
    
    def student_view(self):
        student = Student.query.filter_by(sid=self.user.id).first()
        placed_text = "Yes" if student.placed else "No"
        applications = Application.query.filter_by(student_id=student.id).all()
        application = Application.query.filter_by(student_id=student.id, application_status="accepted").first()
        if student.placed:
            job = Job.query.filter_by(id=application.job_id).first()
            job_title = job.job_title
            company = Company.query.filter_by(id=job.company_id).first()
            company_name = company.company_name
        else:
            job_title = "Not Applicable"
            company_name = "Not Applicable"
        self.view_html = f'''
        <div class="container mt-4 mb-4">
            <div class="card">
                <div class="card-header text-center">
                    <h2 class="mb-0">Student Profile</h2>
                </div>
                <div class="card-body fs-5">
                    <div class="row mb-3">
                        <div class="col mb-2">
                            <strong>Name:</strong> {self.user.fname} {self.user.lname}
                        </div>
                        <div class="col mb-2">
                            <strong>Email:</strong> {self.user.email}
                        </div>
                        <div class="col mb-2">
                            <strong>Username:</strong> {self.user.username}
                        </div>
                        <div class="col mb-2">
                            <strong>University:</strong> {student.university}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-4 mb-2">
                            <strong>Major:</strong> {student.major}
                        </div>
                        <div class="col-4 mb-2">
                            <strong>GPA:</strong> {student.gpa}
                        </div>
                        <div class="col-4 mb-2">
                            <strong>Years of Experience:</strong> {student.years_of_experience}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-4 mb-2">
                            <strong>Placed:</strong> {placed_text}
                        </div>
                        <div class="col-4 mb-2">
                            <strong>Resume:</strong> <a href="/static/{student.resume_path}" target="_blank"><i>{student.resume_path}</i></a>
                        </div>
                        <div class="col-4 mb-2">
                            <strong>Applications number:</strong> {len(applications)}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-4 mb-2">
                            <strong>Job Title:</strong> {job_title}
                        </div>
                        <div class="col-4 mb-2">
                            <strong>Company:</strong> {company_name}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-4 mb-2">
                            <strong>Ban Status:</strong> {"Banned" if self.user.admin_enforced_blacklist_status else "Not Banned"}
                        </div>
                        <div class="col-4 mb-2">
                            <strong>Admin Approval:</strong> {self.user.admin_approval_status.capitalize()}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    '''
            
    def company_view(self):
        company = Company.query.filter_by(company_hr_id=self.user.id).first()
        jobs = Job.query.filter_by(company_id=company.id).all()

        self.view_html = f'''
        <div class="container mt-4 mb-4">
            <div class="card">
                <div class="card-header text-center">
                    <h2 class="mb-0">Company Profile</h2>
                </div>
                <div class="card-body fs-5">
                    <div class="row mb-3">
                        <div class="col-6 mb-2">
                            <strong>HR Name:</strong> {self.user.fname} {self.user.lname}
                        </div>
                        <div class="col-6 mb-2">
                            <strong>Email:</strong> {self.user.email}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-6 mb-2">
                            <strong>Username:</strong> {self.user.username}
                        </div>
                        <div class="col-6 mb-2">
                            <strong>Company Name:</strong> {company.company_name}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-4 mb-2">
                            <strong>Type:</strong> {company.company_type}
                        </div>
                        <div class="col-4 mb-2">
                            <strong>Area:</strong> {company.company_area}
                        </div>
                        <div class="col-4 mb-2">
                            <strong>Jobs Posted:</strong> {len(jobs)}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-12 mb-2">
                            <strong>Description:</strong> {company.company_description}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-6 mb-2">
                            <strong>Website:</strong> <a href="{company.website_url}" target="_blank"><i>{company.website_url}</i></a>
                        </div>
                        <div class="col-6 mb-2">
                            <strong>Ban Status:</strong> {"Banned" if self.user.admin_enforced_blacklist_status else "Not Banned"}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-6 mb-2">
                            <strong>Admin Approval:</strong> {self.user.admin_approval_status.capitalize()}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    '''
        
    def job_view(self):
        company = Company.query.filter_by(id=self.job.company_id).first()
        applications = Application.query.filter_by(job_id=self.job.id).all()
        self.view_html = f'''
        <div class="container mt-4 mb-4">
            <div class="card">
                <div class="card-header text-center">
                    <h2 class="mb-0">Job Profile</h2>
                </div>
                <div class="card-body fs-5">
                    <div class="row mb-3">
                        <div class="col-3 mb-2">
                            <strong>Job Title:</strong> {self.job.job_title}
                        </div>
                        <div class="col-3 mb-2">
                            <strong>Company:</strong> {company.company_name}
                        </div>
                        <div class="col-6 mb-2">
                            <strong>Required Skills:</strong> {self.job.minimum_skills}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-3 mb-2">
                            <strong>Salary Range:</strong> {self.job.salary_range}
                        </div>
                        <div class="col-3 mb-2">
                            <strong>Total applications submitted:</strong> {len(applications)}
                        </div>
                        <div class="col-3 mb-2">
                            <strong>Deadline:</strong> {self.job.deadline}
                        </div>
                        <div class="col-3 mb-2">
                            <strong>Minimum GPA:</strong> {self.job.min_req_gpa}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-6 mb-2">
                            <strong>Description:</strong> {self.job.job_description}
                        </div>
                        <div class="col-3 mb-2">
                            <strong>Location:</strong> {self.job.location}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-6 mb-2">
                            <strong>Admin Approval:</strong> {self.job.admin_approval_status.capitalize()}
                        </div>
                        <div class="col-6 mb-2">
                            <strong>Drive Status:</strong> {"Open" if self.job.job_status else "Closed"}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''

    def application_view(self):
        company = Company.query.filter_by(id=self.job.company_id).first()
        self.view_html = f'''
        <div class="container mt-4 mb-4">
            <div class="card">
                <div class="card-header text-center">
                    <h2 class="mb-0">Application Profile</h2>
                </div>
                <div class="card-body fs-5">
                    <div class="row mb-3">
                        <div class="col-4 mb-2">
                            <strong>Student Name:</strong> {self.student.user.fname} {self.student.user.lname}
                        </div>
                        <div class="col-4 mb-2">
                            <strong>Email:</strong> {self.student.user.email}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-4 mb-2">
                            <strong>University:</strong> {self.student.university}
                        </div>
                        <div class="col-4 mb-2">
                            <strong>Major:</strong> {self.student.major}
                        </div>
                        <div class="col-4 mb-2">
                            <strong>GPA:</strong> {self.student.gpa}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col mb-2">
                            <strong>Years of Experience:</strong> {self.student.years_of_experience}
                        </div>
                        <div class="col mb-2">
                            <strong>Resume:</strong> <a href="/static/{self.student.resume_path}" target="_blank"><i>{self.student.resume_path}</i></a>
                        </div>
                        <div class="col mb-2">
                            <strong>Application Status:</strong> {self.application.application_status.capitalize()}
                        </div>
                        <div class="col mb-2">
                            <strong>Applied Date:</strong> {self.application.date}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-6 mb-2">
                            <strong>Relevant Skills:</strong> {self.application.relevant_skills}
                        </div>
                        <div class="col-6 mb-2">
                            <strong>Cover Letter:</strong> {self.application.cover_letter}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''


    def make_approve_button(self): ## for admin
        approval_status = self.user.admin_approval_status

        approve_disabled = "disabled" if approval_status == "approved" else ""
        not_approve_disabled = "disabled" if approval_status == "not-approved" else ""

        self.make_ban_button()
        self.make_edit_button()
        self.approve_bttn_html = f"""
        <div class="container mb-4">
            <div class="d-flex gap-2 flex-wrap">
                <form method="POST" action="/admin/_approve" class="m-0">
                    <input type="hidden" name="user_id" value="{self.user_id}">
                    <button type="submit" class="btn btn-outline-success" {approve_disabled}>
                        Approve
                    </button>
                </form>

                <form method="POST" action="/admin/_not_approve" class="m-0">
                    <input type="hidden" name="user_id" value="{self.user_id}">
                    <button type="submit" class="btn btn-outline-danger" {not_approve_disabled}>
                        Reject
                    </button>
                </form>

                {self.ban_bttn_html}

                {self.edit_bttn_html}
            </div>
        </div>
        """


    def make_ban_button(self): # for admin
        ban_status = self.user.admin_enforced_blacklist_status

        ban_disabled = "disabled" if ban_status else ""
        unban_disabled = "disabled" if not ban_status else ""

        self.ban_bttn_html = f"""
            <form method="POST" action="/admin/_ban" class="m-0">
                <input type="hidden" name="user_id" value="{self.user_id}">
                <button type="submit" class="btn btn-outline-success" {ban_disabled}>
                    Ban
                </button>
            </form>

            <form method="POST" action="/admin/_unban" class="m-0">
                <input type="hidden" name="user_id" value="{self.user_id}">
                <button type="submit" class="btn btn-outline-danger" {unban_disabled}>
                    Remove Ban
                </button>
            </form>
        """

    def make_edit_button(self): # for admin
        self.edit_bttn_html = f"""
            <form method="GET" action="/admin/edit_user" class="m-0">
                <input type="hidden" name="user_id" value="{self.user_id}">
                <button type="submit" class="btn btn-outline-primary">Edit</button>
            </form>
        """


    def make_job_approve_button(self): ## for admin
        approval_status = self.job.admin_approval_status
        approve_disabled = "disabled" if approval_status == "approved" else ""
        not_approve_disabled = "disabled" if approval_status == "not-approved" else ""
        self.approve_bttn_html = f"""
        <div class="container mb-4">
            <div class="d-flex gap-2 flex-wrap">
                <form method="POST" action="/admin/_approve" class="m-0">
                    <input type="hidden" name="job_id" value="{self.job_id}">
                    <button type="submit" class="btn btn-outline-success" {approve_disabled}>
                        Approve
                    </button>
                </form>
                <form method="POST" action="/admin/_not_approve" class="m-0">
                    <input type="hidden" name="job_id" value="{self.job_id}">
                    <button type="submit" class="btn btn-outline-danger" {not_approve_disabled}>
                        Reject
                    </button>
                </form>
            </div>
        </div>
        """

    def make_job_apply_button(self): ## for student
        self.apply_btn_html = f"""
        <div class="container mb-4">
            <div class="d-flex gap-2 flex-wrap">
                <form method="POST" action="/student/_to_application_form" class="m-0">
                    <input type="hidden" name="job_id" value="{self.job_id}">
                    <button type="submit" class="btn btn-outline-success">Apply</button>
                </form>
            </div>
        </div>
        """
    

    def make_application_accept_reject_button(self): ## for company
        application_status = self.application.application_status
        offer_disabled = "disabled" if application_status in ["withdrawn", "accepted", "offered"] else ""
        reject_disabled = "disabled" if application_status in ["withdrawn", "accepted", "rejected"] else ""
        shortlist_disabled = "disabled" if application_status in ["withdrawn", "accepted", "shortlisted"] else ""
        self.apply_btn_html = f"""
        <div class="container mb-4">
            <div class="d-flex gap-2 flex-wrap">
                <form method="POST" action="/company/_accept_" class="m-0">
                    <input type="hidden" name="application_id" value="{self.application_id}">
                    <button type="submit" class="btn btn-outline-success" {offer_disabled}>Accept</button>
                </form>
                <form method="POST" action="/company/_shortlist_" class="m-0">
                    <input type="hidden" name="application_id" value="{self.application_id}">
                    <button type="submit" class="btn btn-outline-danger" {shortlist_disabled}>Shortlist</button>
                </form>
                <form method="POST" action="/company/_reject_" class="m-0">
                    <input type="hidden" name="application_id" value="{self.application_id}">
                    <button type="submit" class="btn btn-outline-danger" {reject_disabled}>Reject</button>
                </form>
               
            </div>
            </div>
        </div>
        </div>"""

    def make_drive_status_change(self):
        drive_status = self.job.job_status
        open_disabled = "disabled" if drive_status else ""
        close_disabled = "disabled" if not drive_status else ""
        if drive_status:
            message = """<p class="text-danger p-3"> If you close this drive, all pending applications will be rejected.</p>"""
        else:
            message = ""
        self.apply_btn_html = f"""
        <div class="container mb-4">
            <div class="d-flex gap-2 flex-wrap">
                <form method="POST" action="/company/_open_drive" class="m-0">
                    <input type="hidden" name="job_id" value="{self.job_id}">
                    <button type="submit" class="btn btn-outline-success" {open_disabled}>Open Drive</button>
                </form>
                <form method="POST" action="/company/_close_drive" class="m-0">
                    <input type="hidden" name="job_id" value="{self.job_id}">
                    <button type="submit" class="btn btn-outline-danger" {close_disabled}>Close Drive</button>
                </form>
                <form method="GET" action="/company/edit_drive" class="m-0">
                    <input type="hidden" name="job_id" value="{self.job_id}">
                    <button type="submit" class="btn btn-outline-success">Edit Drive</button>
                </form>
            </div>
        </div>
        <div>
        {message}
        </div>
        """

    def make_accept_withdraw_bttn(self): ## for student
        application_status = self.application.application_status 
        accept_disabled = "disabled" if application_status != "offered" else ""
        withdraw_disabled = "disabled" if application_status == "accepted" or application_status == "withdrawn" or application_status == "rejected" else ""
        if application_status == "offered":
            message = """<p class="text-danger p-3"> If you accept this offer, all other applications will be witdrawn.</p>"""
        else:
            message = ""
        self.apply_btn_html = f"""
        <div class="container mb-4">
            <div class="d-flex gap-2 flex-wrap">
                <form method="POST" action="/student/_accept_offer" class="m-0">
                    <input type="hidden" name="application_id" value="{self.application_id}">
                    <button type="submit" class="btn btn-outline-success" {accept_disabled}>Accept Offer</button>
                </form>
                <form method="POST" action="/student/_withdraw" class="m-0">
                    <input type="hidden" name="application_id" value="{self.application_id}">
                    <button type="submit" class="btn btn-outline-danger" {withdraw_disabled}>Withdraw</button>
                </form>
            </div>
        </div>
        <div>
        {message}
        </div>
        """

    def construct_view(self):
        if self.who_is_viewing == "company" and self.is_application:
            self.application_view()
            appli_view = self.view_html
            self.job_view()
            self.make_application_accept_reject_button()
            return self.view_html + appli_view + self.apply_btn_html

        elif self.is_job and self.who_is_viewing == "company":
            self.job_view()
            self.make_drive_status_change()
            return self.view_html + self.apply_btn_html
        
        
        elif self.who_is_viewing == "student" and self.is_job: ### only for open jobs, not for applied jobs
            self.job_view()
            self.make_job_apply_button()
            return self.view_html + self.apply_btn_html
        
        elif self.who_is_viewing == "student" and self.is_application:
            self.application_view()
            appli_view = self.view_html
            self.job_view()
            self.make_accept_withdraw_bttn()
            return self.view_html + appli_view + self.apply_btn_html
        

        #### for admin viewing
        elif self.who_is_viewing == "admin" and self.is_application:
            self.application_view()
            appli_view = self.view_html
            self.job_view()
            return self.view_html + appli_view
        
        elif self.is_job:
            self.job_view()
            self.make_job_approve_button()
            return self.view_html + self.approve_bttn_html
        
        elif self.role == "student":
            self.student_view()
            self.make_approve_button()
            return self.view_html + self.approve_bttn_html
        elif self.role == "HR":
            self.company_view()
            self.make_approve_button()
            return self.view_html + self.approve_bttn_html
        else:
            return None