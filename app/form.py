from wtforms import Form, BooleanField, StringField, validators, DateTimeField, IntegerField     # Form fields
from wtforms.fields.html5 import DateField                                          # Special form field
from model import Calendar


class RegistrationForm(Form):
    nickname = StringField('Username', [validators.Length(min=3, max=10)])
    birthday  = DateField('Your date of birth')
    accept_eula = BooleanField('I accept the End User License Agreement', [validators.DataRequired()])


def enabled_calendars():
    return Calendar.query.all()


class NewEventForm(Form):
    #from wtforms.ext.sqlalchemy.fields import QuerySelectField
    calendar = IntegerField('Calendar ID') #QuerySelectField(query_factory=enabled_calendars, allow_blank=True)
    start = DateField('First day')
    end = DateField('Last day')
    note = StringField('Note')
