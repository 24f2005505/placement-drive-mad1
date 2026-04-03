from make_app import init_app
from make_form import make_form
from make_login import make_login
import make_admin_dashboard 
from flask import render_template
from create_aritifical_data import create_artificial_data
app = init_app()

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

## from hmtl forms saves data and handles everything
make_form(app)
make_login(app)
make_admin_dashboard.make_dashboard(app)

create_artificial_data(app) ## create some artificial data for testing (only creates data if the database is empty, so safe to run multiple times)
print("Artificial data created (if database was empty). Remove it later.")


if __name__ == '__main__':
    app.run(debug=True)

    