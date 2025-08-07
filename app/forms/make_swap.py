from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField
from wtforms.validators import DataRequired, Length

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
        'Describe your swap (optional)',
        validators=[Length(max=300)]
    )
