from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField
from wtforms.validators import DataRequired, Length

class AddSkillForm(FlaskForm):
    name = SelectField(
        'Skill Name',
        validators=[DataRequired()],
        coerce=str
    )

    category = SelectField(
        'Category',
        validators=[DataRequired()],
        coerce=str
    )

    description = TextAreaField(
        'Description',
        validators=[DataRequired(), Length(min=20, max=500)],
        render_kw={"placeholder": "Describe your skill (what exactly can you do?)..."}
    )
