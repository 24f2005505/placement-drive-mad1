from flask import render_template
from model import db, Company, User, Student, Job


def get__stats():
    stats = {}
    top_companies = {}
    top_companies_area={}
    top_companies_desc ={}
    companies = Company.query.all() ## this is deliberately a misleading advertisement
    if companies:
        for c in companies:
            apps = 0
            jobs = c.jobs
            for jb in jobs:
                apps += len(jb.applications)
            top_companies[c.company_name] = apps
            top_companies_desc[c.company_description] = apps
            top_companies_area[c.company_area] = apps
            
        top_companies = sorted(top_companies.items(), key=lambda x: x[1], reverse=True)[:4]
        top_companies_desc = sorted(top_companies_desc.items(), key=lambda x: x[1], reverse=False)[:4]
        top_companies_area = sorted(top_companies_area.items(), key=lambda x: x[1], reverse=False)[:4]
        top_companies = [c[0] for c in top_companies]
        top_companies_desc = [c[0] for c in top_companies_desc]
        top_companies_area = [c[0] for c in top_companies_area]
    else:
        top_companies = ["No companies found", "No companies found", "No companies found", "No companies found"]
        top_companies_desc = ["No companies found", "No companies found", "No companies found", "No companies found"]
        top_companies_area = ["No companies found", "No companies found", "No companies found", "No companies found"]
    
    
    stats['top_companies'] = top_companies
    stats['top_companies_desc'] = top_companies_desc
    stats['top_companies_area'] = top_companies_area

    stats['total_students'] = User.query.filter_by(role="student").count() if User.query.filter_by(role="student").count()  else 0
    stats['total_companies'] = User.query.filter_by(role="HR").count() if User.query.filter_by(role="HR").count() else 0
    stats['total_students_placed'] = Student.query.filter_by(placed=True).count() if  Student.query.filter_by(placed=True).count() else 0
    stats['total_drives'] = Job.query.count() if Job.query.count() else 0
    return stats

def make_homepage(app):
    @app.route('/index')
    @app.route('/')
    def index():
        stats = get__stats()
        return render_template('index.html', stats =stats) 