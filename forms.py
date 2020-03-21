from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length


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
