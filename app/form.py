from wtforms import Form, BooleanField, StringField, validators, DateTimeField, IntegerField     # Form fields
from wtforms.fields.html5 import DateField                                          # Special form field
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
    birthday  = DateField('Your date of birth')
    accept_eula = BooleanField('I accept the End User License Agreement', [validators.DataRequired()])


class QueryCalendars(Form):
    calendar_list = QuerySelectField(
        'name',
        query_factory=lambda: Calendar.query.all(),
        allow_blank=False
    )

# Adding new event form
class NewEventForm(Form):
    #from wtforms.ext.sqlalchemy.fields import QuerySelectField
    #calendar = IntegerField('Calendar ID') #QuerySelectField(query_factory=enabled_calendars, allow_blank=True)
    calendar_list = QuerySelectField(
        'Calendar',
        query_factory=lambda: Calendar.query.all(),
        allow_blank=False
    )
    start = DateField('First day')
    end = DateField('Last day')
    note = StringField('Note')
