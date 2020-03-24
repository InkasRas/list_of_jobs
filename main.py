import sqlalchemy
import datetime
import db_session
import os
from __all_models import User, Jobs
from flask import Flask, render_template, redirect, url_for, session, request, make_response, abort
from forms import RegisterForm, LoginForm, NewJobForm
from flask_login import login_user, LoginManager, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['CSRF_ENABLED'] = True
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    sesion = db_session.create_session()
    return sesion.query(User).get(id)


@app.route('/')
def base():
    sesion = db_session.create_session()
    jobs = {'jobs': []}
    for job in sesion.query(Jobs):
        job_json = {'job': {}}
        job_json['job']['user'] = job.tm_leader
        job_json['job']['job'] = job
        if current_user.is_authenticated and (current_user.id == job.tm_leader.id or current_user.id == job.creator_id):
            job_json['job']['btns'] = True
        jobs['jobs'].append(job_json)
    return render_template('jobs.html', jobs=jobs)


@app.route('/success')
def success():
    return '<h1>Success</h1>'


@login_manager.unauthorized_handler
def unann():
    resp = make_response(redirect(url_for('login', next=request.url, message='Login required')))
    return resp


@app.route('/login', methods=['POST', 'GET'])
def login():
    red_path = request.args.get('next', '/')
    if current_user.is_authenticated:
        return redirect(red_path)
    form = LoginForm()
    if form.validate_on_submit():
        sesion = db_session.create_session()
        user = sesion.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            if not form.remember_me.data:
                session['remeber_mme'] = 0
            else:
                session['remeber_mme'] = 1
            login_user(user, remember=form.remember_me.data)
            return redirect(red_path)
        return render_template('login.html', form=form, title='Login')
    return render_template('login.html', form=form, title='Login', message=request.args.get('message', ''))


def check_job(form, template):
    datetime1 = datetime.datetime.combine(form.start_date.data, datetime.datetime.min.time())
    datetime2 = datetime.datetime.combine(form.end_date.data, datetime.datetime.min.time())
    if datetime2 <= datetime1:
        form.end_date.errors.append('Date should be valid')
        return {'response': (template, form)}
    sesion = db_session.create_session()
    if not sesion.query(User).get(form.team_leader.data):
        form.team_leader.errors.append('Team leader does not exist')
        return {'response': (template, form)}
    return {'response': ['OK', datetime1, datetime2]}


@app.route('/deletejob/<int:job_id>', methods=['GET', 'POST'])
@login_required
def delete_job(job_id):
    sesion = db_session.create_session()
    job = sesion.query(Jobs).get(job_id)
    if not job:
        abort(404)
    if job.tm_leader.id != current_user.id and job.creator_id != current_user.id:
        abort(403)
    sesion.delete(job)
    sesion.commit()
    return redirect('/')


@app.route('/editjob/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    form = NewJobForm()
    form.submit.label.text = 'Edit'
    sesion = db_session.create_session()
    job = sesion.query(Jobs).get(job_id)
    if not job:
        abort(404)
    if request.method == 'GET':
        form.collaborator.data = 'None'
        form.job.data = job.job
        form.work_size.data = job.work_size
        form.team_leader.data = job.team_leader
        form.start_date.data = job.start_date
        form.end_date.data = job.end_date
        form.is_finished.data = job.is_finished
    if form.validate_on_submit():
        resp = check_job(form, 'editjob.html')
        if resp['response'][0] != 'OK':
            return render_template(resp['response'][0], title='Job edit', form=resp['response'][1])
        job.team_leader = form.team_leader.data
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborator.data
        job.start_date = resp['response'][1]
        job.end_date = resp['response'][2]
        job.is_finished = form.is_finished.data
        sesion.commit()
        sesion.close()
        return redirect('/')
    return render_template('newjob.html', title='Job edit', form=form)


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def new_job():
    form = NewJobForm()
    if form.validate_on_submit():
        resp = check_job(form, 'newjob.html')
        if resp['response'][0] != 'OK':
            return render_template(resp['response'][0], title='New job', form=resp['response'][1])
        sesion = db_session.create_session()
        job = Jobs(team_leader=form.team_leader.data,
                   job=form.job.data,
                   work_size=form.work_size.data,
                   collaborators=form.collaborator.data,
                   start_date=resp['response'][1],
                   end_date=resp['response'][2],
                   is_finished=form.is_finished.data,
                   creator_id=current_user.id)
        sesion.add(job)
        sesion.commit()
        sesion.close()
        return redirect('/')
    return render_template('newjob.html', title='New job', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        sesion = db_session.create_session()
        if sesion.query(User).filter(User.email == form.email.data).first():
            form.email.errors.append('Email already exists')
            return render_template('register.html', form=form, title='Register')
        elif sesion.query(User).filter(User.username == form.login.data).first():
            form.login.errors.append('Username already exists')
            return render_template('register.html', form=form, title='Register')
        new_user = User(surname=form.surname.data,
                        name=form.name.data,
                        email=form.email.data,
                        age=form.age.data,
                        position=form.position.data,
                        speciality=form.speciality.data,
                        address=form.address.data,
                        username=form.login.data)
        new_user.set_password(form.password.data)
        sesion.add(new_user)
        sesion.commit()
        return redirect('/')
    return render_template('register.html', form=form, title='Register')


@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html', title='Not found', message='Not found')


@app.errorhandler(403)
def forbidden(error):
    return render_template('not_found.html', title='Forbidden', message='Forbidden')


if __name__ == '__main__':
    db_session.global_init('blogs.sqlite')
    app.run()
