from wtforms import Form, TextField, TextAreaField, PasswordField, validators

class LoginForm(Form):
    email = TextField("Email", [validators.Required(), validators.Email()])
    password = PasswordField("Password", [validators.Required()])
