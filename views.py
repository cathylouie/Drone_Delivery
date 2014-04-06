from flask import Flask, render_template, redirect, request, g, session, url_for, flash
from model import User, Address, Order, Duck, DuckOrder
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from flaskext.markdown import Markdown
import config
import forms
import model
import json

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

@app.route("/testsuite")
def testsuite():

    return render_template("testsuite.html")

@app.route("/earth", methods=["POST"])
def earth():
    coords_list = json.loads(request.form.get("coords",[]))
    
    return render_template("earth.html", coords_list=coords_list)

@app.route("/SFmap")
def SFmap():
    a = model.session.query(Address).filter_by(user_id=current_user.id).one()
    lat = a.lat
    lng = a.lng
    
    return render_template("SFmap.html", lat = lat, lng = lng)

@app.route("/")
def storeFront():
    return render_template("front_page.html")

@app.route("/duck_list")
def duck_list():
    return render_template("duck_list.html")

@app.route("/view_order")
@login_required
def view_order():
    duck_id = request.args.get("duck")
    d = model.session.query(Duck).get(duck_id)
    pic = d.pic
    name = d.name
    price = d.price
    bio = d.bio
    
    return render_template("view_order.html", duck_id=request.args.get("duck"),
                                                pic = pic,
                                                name = name,
                                                price = price,
                                                bio = bio)

@app.route("/confirm_order", methods=["POST"])
@login_required
def confirm_order():
    duck_id = request.args.get("duck")
    new_order = Order(user_id=current_user.id)
    model.session.add(new_order)
    model.session.commit()
    #This will request the new_order.id that was just commited for the DuckOrder tables 
    model.session.refresh(new_order)

    qty = request.form.get("qty")

    new_duckorder = DuckOrder(order_id=new_order.id, duck_id=request.args.get("duck"), qty=qty)

    model.session.add(new_duckorder)
    model.session.commit()

    a = model.session.query(Address).filter_by(user_id=current_user.id).one()
    address1 = a.address1
    address2 = a.address2
    city = a.city
    state = a.state
    zipcode = a.zipcode
    country = a.country
    lat = a.lat
    lng = a.lng

    if a.lat <= 37.8 and a.lat >= 37.78 and a.lng <= -122.386 and a.lng >= -122.436:
        return render_template("confirm_order2.html", duck_id=request.args.get("duck"), 
                                                    order_id=new_order.id,
                                                    address1 = a.address1,
                                                    address2 = a.address2,
                                                    city = a.city,
                                                    state = a.state,
                                                    zipcode = a.zipcode,
                                                    country = a.country)
    return render_template("confirm_order.html", duck_id=request.args.get("duck"), 
                                                    order_id=new_order.id,
                                                    address1 = a.address1,
                                                    address2 = a.address2,
                                                    city = a.city,
                                                    state = a.state,
                                                    zipcode = a.zipcode,
                                                    country = a.country)
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("storeFront"))

@app.route("/login")
def login():
    if session.get('user_id', None):
         return redirect(url_for("view_order", duck=request.args.get("duck")))
    if request.args.get("duck"):
        return render_template("login.html", duck=request.args.get("duck"))
    return render_template("login.html", duck=None)

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

    return redirect(url_for("view_order", duck=request.args.get("duck")))

@app.route("/new_user_reg")
def display_reg():
    if request.args.get("duck"):
        return render_template("new_user_reg.html", duck=request.args.get("duck"))
    return render_template("new_user_reg.html", duck=None)

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
    zipcode = int(request.form.get("zipcode")) if request.form.get("zipcode") else None
    country = request.form.get("country")
    phone = int(request.form.get("phone")) if request.form.get("phone") else None
    
#Verification if user already exists
    existing = User.query.filter_by(email=email).first()

    if existing:
        flash("This email already exists,Please select another one!")
        return redirect(url_for("new_user_reg")) #redirect back to sign up page
    elif password != password_ver:
        flash("Your password do not match")
        return redirect(url_for("new_user_reg")) #redirect back to sign up page
    else:
        new_user = User(email=email, firstname = firstname, surname = surname)#make the new_user object
        new_user.set_password(password)

        # Queue it up to be put into the database
        model.session.add(new_user)

        # create a variable to use for input into the addresses table and geocoding
        a = Address(    email = email, 
                        address1 = address1, 
                        address2 = address2,
                        city = city,
                        state = state,
                        zipcode = zipcode,
                        country = country,
                        phone = phone)
        #get LagLng from google api for address input by user in this session
        a.geocode()
        # append address info including latlng of the new user to the adresses table
        new_user.addresses.append(a)

        # Now we've got all the stuff the database wants to put in the addresses table,
        # we can add and commit everything to the database.
        model.session.commit()

        login_user(new_user)
        
        return redirect(url_for("view_order", duck=request.args.get("duck")))

if __name__ == "__main__":
    app.run(debug=True)
