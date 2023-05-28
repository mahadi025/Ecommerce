from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, BooleanField, FileField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms.validators import InputRequired
from wtforms import StringField, PasswordField
from flask_admin.form import FileUploadField


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[
                       DataRequired(), NumberRange(min=0)])
    digital = BooleanField('Digital')
    image = FileField('Image', validators=[Optional()])


class UserRegistrationLoginForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password1 = PasswordField('Password1', validators=[InputRequired()])
    password2 = PasswordField('Password2', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])


class CustomerEditForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])
    image = FileField('Image', default='DefaultProfilePic.jpg')
    phone = StringField('Phone', default="+880....")


class UserLoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])


class CheckOutForm(FlaskForm):
    pass
