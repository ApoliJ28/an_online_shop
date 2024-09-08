from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf import FlaskForm

# TODO: Create a RegisterForm to register new users

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    mail = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("SING ME UP!")

# TODO: Create a LoginForm to login existing users


class LoginForm(FlaskForm):
    mail = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("LET ME IN!")