import sqlalchemy
import datetime
import db_session
from __all_models import User, Jobs
from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def base():
    session = db_session.create_session()
    jobs = []
    for job in session.query(Jobs):
        user=session.query(User).filter(User.id==job.team_leader).first()
        jobs.append((job,' '.join([user.name,user.surname])))

    return render_template('jobs.html',jobs=jobs,session=session)

if __name__ == '__main__':
    db_session.global_init('blogs.sqlite')
    app.run()
