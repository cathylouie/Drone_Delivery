from flask import Flask, render_template, redirect, request, g, session, url_for, flash
from model import User, Address, Order
from flask.ext.login import LoginManager, login_required, login_user, current_user
from flaskext.markdown import Markdown
import config
import forms
import model

app = Flask(__name__)
app.config.from_object(config)

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# End login stuff

# Adding markdown capability to the app
Markdown(app)

@app.route("/")
def storeFront():
    return render_template("front_page.html")

@app.route("/duck_list")
def duck_list():
    return render_template("duck_list.html")

@app.route("/view_order1")
@login_required
def view_order1():
    return render_template("view_order1.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def authenticate():
    form = forms.LoginForm(request.form)
    if not form.validate():
        flash("Incorrect username or password") 
        return render_template("login.html")

    email = form.email.data
    password = form.password.data

    user = User.query.filter_by(email=email).first()

    if not user or not user.authenticate(password):
        flash("Incorrect username or password") 
        return render_template("login.html")

    login_user(user)
    return redirect(request.args.get("next", url_for("view_order1.html")))

@app.route("/new_user_reg")
def display_reg():
    return render_template("new_user_reg.html")    

@app.route("/new_user_reg", methods=["POST"])
def new_user_reg():
    email = request.form.get("email")
    password = request.form.get("password")
    password_ver = request.form.get("password_ver")
    firstname = request.form.get("firstname")
    surname = request.form.get("surname")
    address1 = request.form.get("address1")
    address2 = request.form.get("address2")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")
    country = request.form.get("country")
    phone = request.form.get("phone")
    kind = request.form.get("kind") #home or delivery
    
#Verification if user already exists
    existing = User.query.filter_by(email=email).first()

    if existing:
        flash("This email already exists,Please select another one!")
        return redirect(url_for("new_user_reg")) #redirect back to sign up page
    elif password != password_ver:
        flash("Your password do not match")
        return redirect(url_for("new_user_reg")) #redirect back to sign up page
    else:
        new_user = User(email=email, password=password, firstname = firstname, surname = surname)
        new_user_address = Address(email = email, 
                                        address1 = address1, 
                                        address2 = address2,
                                        city = city,
                                        state = state,
                                        zipcode = zipcode,
                                        country = country,
                                        phone = phone,
                                        kind = kind)

        model.session.add(new_user)
        model.session.add(new_user_address)
        model.session.commit()
        # model.session['user_id'] = new_user.id
        return redirect(url_for("view_order1.html")) 


if __name__ == "__main__":
    app.run(debug=True)
