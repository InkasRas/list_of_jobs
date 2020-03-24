import sqlalchemy
import datetime
import db_session
from __all_models import User, Jobs
from flask import Flask, render_template, redirect, url_for, session, request, make_response
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
    jobs = []
    for job in sesion.query(Jobs):
        user = sesion.query(User).filter(User.id == job.team_leader).first()
        jobs.append((job, ' '.join([user.name, user.surname])))

    return render_template('jobs.html', jobs=jobs, session=sesion)


@app.route('/success')
def success():
    print(session)
    return '<h1>Success</h1>'


@login_manager.unauthorized_handler
def unann():
    print(request, request.path)
    resp = make_response(redirect('/login'))
    resp.set_cookie('message', 'Login required')
    resp.set_cookie('red_path', request.path)
    return resp


@app.route('/login', methods=['POST', 'GET'])
def login():
    red_path = request.cookies.get('red_path', '/')
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
            print(dir(current_user))
            return redirect(red_path)
        return render_template('login.html', form=form, title='Login')
    return render_template('login.html', form=form, title='Login', message=request.cookies.get('message', ''))


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def new_job():
    form = NewJobForm()
    if form.validate_on_submit():
        print('POST')
        datetime1 = datetime.datetime.combine(form.start_date.data, datetime.datetime.min.time())
        datetime2 = datetime.datetime.combine(form.end_date.data, datetime.datetime.min.time())
        print(datetime1, datetime2, datetime1 < datetime2)
        if datetime2 <= datetime1:
            form.end_date.errors.append('Date should be valid')
            return render_template('newjob.html', form=form)
        sesion = db_session.create_session()
        if not sesion.query(User).get(form.team_leader.data):
            form.team_leader.errors.append('Team leader does not exist')
            return render_template('newjob.html', form=form)
        job = Jobs(team_leader=form.team_leader.data,
                   job=form.job.data,
                   work_size=form.work_size.data,
                   collaborators=form.collaborator.data,
                   start_date=datetime1,
                   end_date=datetime2,
                   is_finished=form.is_finished.data)
        sesion.add(job)
        sesion.commit()
        sesion.close()
        return redirect('/')
    return render_template('newjob.html', form=form)


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
    return render_template('not_found.html', title='Not found')


if __name__ == '__main__':
    db_session.global_init('blogs.sqlite')
    app.run()
