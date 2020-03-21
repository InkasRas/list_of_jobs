import sqlalchemy
import datetime
import db_session
from __all_models import User, Jobs
from flask import Flask, render_template, request, redirect, url_for
from forms import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['CSRF_ENABLED'] = True


@app.route('/')
def base():
    session = db_session.create_session()
    jobs = []
    for job in session.query(Jobs):
        user = session.query(User).filter(User.id == job.team_leader).first()
        jobs.append((job, ' '.join([user.name, user.surname])))

    return render_template('jobs.html', jobs=jobs, session=session)


@app.route('/success')
def success():
    return '<h1>Success</h1>'


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(User).filter(User.email==form.email.data).first():
            form.email.errors.append('Email already exists')
            return render_template('register.html',form=form,title='Register')
        elif session.query(User).filter(User.username==form.login.data).first():
            form.login.errors.append('Username already exists')
            return render_template('register.html',form=form,title='Register')
        new_user = User(surname=form.surname.data,
                        name=form.name.data,
                        email=form.email.data,
                        age=form.age.data,
                        position=form.position.data,
                        speciality=form.speciality.data,
                        address=form.address.data,
                        username=form.login.data)
        new_user.set_password(form.password.data)
        session.add(new_user)
        session.commit()
        return redirect('/success')
    return render_template('register.html', form=form, title='Register')


if __name__ == '__main__':
    db_session.global_init('blogs.sqlite')
    app.run()
