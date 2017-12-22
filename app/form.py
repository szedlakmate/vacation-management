import datetime
from wtforms import Form, BooleanField, StringField, validators     # Form fields
from wtforms.fields.html5 import DateField                          # Special form field
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from model import Calendar

# *************************************************
#                FORM DESCRIPTIONS
# *************************************************

# This file holds all the form compositions.
# New forms shall be registered here


# User registration form
class RegistrationForm(Form):
    nickname = StringField('Username', [validators.Length(min=3, max=10)])
    birthday = DateField('Your date of birth', [validators.DataRequired()])
    accept_eula = BooleanField('I accept the End User License Agreement', [validators.DataRequired()])

    def post_validate(self):
        if not Form.validate(self):
            return False
        valid = True
        if not (datetime.datetime.now().year - self.birthday.data.year >= 18):
            valid = False
            self.birthday.errors.append("You are too young")
        elif not (datetime.datetime.now().year - self.birthday.data.year < 130):
            valid = False
            self.birthday.errors.append("Your age seems to be unreal")
        return valid


class QueryCalendars(Form):
    calendar_list = QuerySelectField('name',
        query_factory=lambda: Calendar.query.all(),
        allow_blank=False
    )


# Adding new event form
class NewEventForm(Form):
    calendar_list = QuerySelectField(
        'Calendar',
        [validators.DataRequired()],
        query_factory=lambda: Calendar.query.all(),
        allow_blank=False
    )
    start = DateField('First day', [validators.DataRequired()])
    end = DateField('Last day', [validators.DataRequired()])
    note = StringField('Note')

    def validate(self):
        if not Form.validate(self):
            return False
        if self.start.data > self.end.data:
            self.start.errors.append("The end date must not be earlier than the start date")
            return False
        else:
            return True
