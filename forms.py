from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateField, DateTimeField, \
    TextAreaField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
import datetime


def age_test(form, field):
    if int(field.data) < 18:
        raise ValidationError('Age less than 18')


class RegisterForm(FlaskForm):
    valids = [DataRequired()]
    email = StringField('Email', validators=valids + [Email()])
    password = PasswordField('Password', validators=valids + [Length(min=8, max=float('inf'),
                                                                     message=f'Length from 8')])
    password_again = PasswordField('Password again',
                                   validators=valids + [EqualTo('password', message='Passwords must match')])
    login = StringField('Login', validators=valids)
    surname = StringField('Surname', validators=valids)
    name = StringField('Name', validators=valids)
    age = IntegerField('Age', validators=valids + [age_test])
    position = StringField('Position', validators=valids)
    speciality = StringField('Speciality', validators=valids)
    address = StringField('Address', validators=valids)
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me', default=False)
    submit = SubmitField('Login')


class NewJobForm(FlaskForm):
    team_leader = IntegerField('Team leader id', validators=[DataRequired()])
    job = TextAreaField('Job description', validators=[DataRequired()])
    work_size = FloatField('Work size', validators=[DataRequired()])
    collaborator = StringField('Collaborators', validators=[DataRequired()])
    start_date = DateField('Start date', default=datetime.datetime.today(), format='%Y-%m-%d')
    end_date = DateField('End date', default=datetime.datetime.today(), format='%Y-%m-%d')
    is_finished = BooleanField('Is finished', default=False)
    submit = SubmitField('Add job')
