from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length


class Login(FlaskForm):
    account = StringField(u'Account', validators=[DataRequired()])
    password = PasswordField(u'Password', validators=[DataRequired()])
    submit = SubmitField(u'Log In')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'Old Password', validators=[DataRequired()])
    password = PasswordField(u'New Password', validators=[DataRequired(), EqualTo('password2', message=u'The two passwords must match!')])
    password2 = PasswordField(u'Confirm New Password', validators=[DataRequired()])
    submit = SubmitField(u'Confirm Change')


class EditInfoForm(FlaskForm):
    name = StringField(u'Username', validators=[Length(1, 32)])
    submit = SubmitField(u'Submit')


class SearchBookForm(FlaskForm):
    methods = [('book_name', 'Book Title'), ('author', 'Author'), ('class_name', 'Category'), ('isbn', 'ISBN')]
    method = SelectField(choices=methods, validators=[DataRequired()], coerce=str)
    content = StringField(validators=[DataRequired()])
    submit = SubmitField('Search')


class SearchStudentForm(FlaskForm):
    card = StringField(validators=[DataRequired()])
    submit = SubmitField('Search')


class StoreForm(FlaskForm):
    barcode = StringField(validators=[DataRequired(), Length(6)])
    isbn = StringField(validators=[DataRequired(), Length(13)])
    location = StringField(validators=[DataRequired(), Length(1, 32)])
    submit = SubmitField(u'Submit')


class NewStoreForm(FlaskForm):
    isbn = StringField(validators=[DataRequired(), Length(13)])
    book_name = StringField(validators=[DataRequired(), Length(1, 64)])
    press = StringField(validators=[DataRequired(), Length(1, 32)])
    author = StringField(validators=[DataRequired(), Length(1, 64)])
    class_name = StringField(validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField(u'Submit')


class BorrowForm(FlaskForm):
    card = StringField(validators=[DataRequired()])
    book_name = StringField(validators=[DataRequired()])
    submit = SubmitField(u'Search')
