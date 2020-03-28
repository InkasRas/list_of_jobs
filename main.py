import sqlalchemy
import datetime
import db_session
import os
from __all_models import User, Jobs, Departments, Category
from flask import Flask, render_template, redirect, url_for, session, request, make_response, abort
from forms import RegisterForm, LoginForm, NewJobForm, NewDepartmentForm
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


@app.route('/base')
def base():
    sesion = db_session.create_session()
    if request.args.get('type', 'job') == 'dep':
        print()
        deprts = {'deps': []}
        for dep in sesion.query(Departments):
            dep_json = {'dep': {}}
            dep_json['dep']['user'] = dep.chief_m
            dep_json['dep']['dep'] = dep
            if current_user.is_authenticated and current_user.id == dep.chief_m.id:
                dep_json['dep']['btns'] = True
            deprts['deps'].append(dep_json)
        return render_template('jobs.html', type='dep', deprts=deprts, ad_tit='Departments')
    else:
        jobs = {'jobs': []}
        for job in sesion.query(Jobs):
            job_json = {'job': {}}
            job_json['job']['user'] = job.tm_leader
            job_json['job']['job'] = job
            if current_user.is_authenticated and (
                    current_user.id == job.tm_leader.id or current_user.id == job.creator_id):
                job_json['job']['btns'] = True
            jobs['jobs'].append(job_json)
        return render_template('jobs.html', jobs=jobs, type='job', ad_tit='Jobs')


@app.route('/')
def basee():
    return redirect(url_for('base', type='job'))


@app.route('/joblist')
def joblist():
    return redirect(url_for('base', type='job'))


@app.route('/deplist')
def deplist():
    return redirect(url_for('base', type='dep'))


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


def check_new_dep(form: NewDepartmentForm):
    sesion = db_session.create_session()
    if not sesion.query(User).get(form.chief.data):
        form.chief.errors.append('Chief does not exist')
        sesion.close()
        return {'response': form}
    sesion.close()
    return {'response': 'OK'}


def check_cat_exists(cat_id):
    sesion = db_session.create_session()
    if not sesion.query(Category).filter(Category.cat_id == cat_id).first():
        sesion.add(Category(cat_id=cat_id))
        sesion.commit()
        sesion.close()


@app.route('/delete/<type>/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_item(type, id):
    sesion = db_session.create_session()
    if type == 'job':
        item = sesion.query(Jobs).get(id)
    elif type == 'dep':
        item = sesion.query(Departments).get(id)
    if not item:
        abort(404)
    if type == 'job' and item.tm_leader.id != current_user.id and item.creator_id != current_user.id:
        abort(403)
    elif type == 'dep' and item.chief_m.id != current_user.id:
        abort(403)
    sesion.delete(item)
    sesion.commit()
    return redirect('/')


@app.route('/edit/<type>/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(type, id):
    if type == 'job':
        form = NewJobForm()
        form.submit.label.text = 'Edit'
        sesion = db_session.create_session()
        job = sesion.query(Jobs).get(id)
        if not job:
            abort(404)
        if request.method == 'GET':
            form.collaborator.data = 'None'
            form.job.data = job.job
            form.work_size.data = job.work_size
            form.team_leader.data = job.team_leader
            form.start_date.data = job.start_date
            form.end_date.data = job.end_date
            if len(job.categories) > 0:
                form.category_id.data = job.categories[0].cat_id
            form.is_finished.data = job.is_finished
        if form.validate_on_submit():
            resp = check_job(form, 'newjob.html')
            if resp['response'][0] != 'OK':
                return render_template(resp['response'][0], add_title='Job edit', title='Job edit',
                                       form=resp['response'][1])
            job.team_leader = form.team_leader.data
            job.job = form.job.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborator.data
            job.start_date = resp['response'][1]
            job.end_date = resp['response'][2]
            job.is_finished = form.is_finished.data
            check_cat_exists(form.category_id.data)
            job.categories.clear()
            job.categories.append(sesion.query(Category).filter(Category.cat_id == form.category_id.data).first())
            sesion.commit()
            sesion.close()
            return redirect('/')
        return render_template('newjob.html', add_title='Edit job', title='Job edit', form=form)
    elif type == 'dep':
        form = NewDepartmentForm()
        form.submit.label.text = 'Edit'
        sesion = db_session.create_session()
        dep = sesion.query(Departments).get(id)
        if not dep:
            abort(404)
        if request.method == 'GET':
            form.chief.data = dep.chief
            form.email.data = dep.email
            form.members.data = dep.members
            form.title.data = dep.title
        if form.validate_on_submit():
            resp = check_new_dep(form)
            if resp['response'] != 'OK':
                return render_template('newjob.html', add_title='Dep. edit', title='Dep. edit', form=resp['response'])
            dep.title = form.title.data
            dep.members = form.members.data
            dep.chief = form.chief.data
            dep.email = form.email.data
            sesion.commit()
            sesion.close()
            return redirect('/')
        return render_template('newjob.html', add_title='Dep. edit', title='Dep. edit', form=form)


@app.route('/adddepartment', methods=['GET', 'POST'])
@login_required
def new_department():
    form = NewDepartmentForm()
    if form.validate_on_submit():
        resp = check_new_dep(form)
        if resp['response'] != 'OK':
            return render_template('newjob.html', add_title='New department', form=form, title='New department')
        sesion = db_session.create_session()
        department = Departments(title=form.title.data,
                                 chief=form.chief.data,
                                 members=form.members.data,
                                 email=form.email.data)
        sesion.add(department)
        sesion.commit()
        sesion.close()
        return redirect('/')
    return render_template('newjob.html', add_title='New department', form=form, title='New department')


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def new_job():
    form = NewJobForm()
    if form.validate_on_submit():
        resp = check_job(form, 'newjob.html')
        if resp['response'][0] != 'OK':
            return render_template(resp['response'][0], add_title='New job', title='New job', form=resp['response'][1])
        sesion = db_session.create_session()
        category_id = form.category_id.data
        check_cat_exists(category_id)
        sesion = db_session.create_session()
        categ = sesion.query(Category).filter(Category.cat_id == category_id).first()
        print(categ)
        job = Jobs(team_leader=form.team_leader.data,
                   job=form.job.data,
                   work_size=form.work_size.data,
                   collaborators=form.collaborator.data,
                   start_date=resp['response'][1],
                   end_date=resp['response'][2],
                   is_finished=form.is_finished.data,
                   creator_id=current_user.id)
        job.categories.append(categ)
        sesion.add(job)
        sesion.commit()
        sesion.close()
        return redirect('/')
    return render_template('newjob.html', add_title='New job', title='New job', form=form)


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
