from bson import Regex
from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class SignupForm(FlaskForm):
    name = StringField(
        'Full Name (first last)',
        validators=[DataRequired(), Length(min=2, max=100)]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    submit = SubmitField('Log In')


class AddSkillForm(FlaskForm):
    name = SelectField(
        'Skill Name',
        validators=[DataRequired()],
        coerce=str
    )

    category = SelectField(
        'Category',
        validators=[
            DataRequired()],
        coerce=str
    )

    description = TextAreaField(
        'Description',
        validators=[DataRequired(), Length(min=20, max=500)],
        render_kw={"placeholder": "Describe your skill (what exactly can you do?)..."}
    )
    

class MakeSwapForm(FlaskForm):
    desired_skill_name = SelectField(
        'What skill do you want to swap with?',
        validators=[DataRequired()],
        coerce=str
    )
    offered_skill_id = SelectField(
        'Select one of your skills to offer',
        validators=[DataRequired()],
         coerce=str
        )
    description = TextAreaField(
        'Describe your swap (optional)', validators=[Length(min=20, max=300), DataRequired()]
        )




