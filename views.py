from flask import Flask, render_template, redirect, request, g, session, url_for, flash
from model import User, Address, Order, Duck, DuckOrder
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

@app.route("/SFmap")
def SFmap():
    return render_template("SFmap.html")

@app.route("/path_finding")
def pathFinding():
    return render_template("pathF.html")

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
    d = model.postgres_session.query(Duck).get(duck_id)
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
    model.postgres_session.add(new_order)
    model.postgres_session.commit()
    #This will request the new_order.id that was just commited for the DuckOrder tables 
    model.postgres_session.refresh(new_order)

    qty = request.form.get("qty")

    new_duckorder = DuckOrder(order_id=new_order.id, duck_id=request.args.get("duck"), qty=qty)

    model.postgres_session.add(new_duckorder)
    model.postgres_session.commit()

    a = model.postgres_session.query(Address).filter_by(user_id=current_user.id).one()
    address1 = a.address1
    address2 = a.address2
    city = a.city
    state = a.state
    zipcode = a.zipcode
    country = a.country

    return render_template("confirm_order.html", duck_id=request.args.get("duck"), 
                                                    order_id=new_order.id,
                                                    address1 = a.address1,
                                                    address2 = a.address2,
                                                    city = a.city,
                                                    state = a.state,
                                                    zipcode = a.zipcode,
                                                    country = a.country)
    #return redirect(url_for("confirm_order", duck_id=request.args.get("duck"), order_id=new_order.id))

@app.route("/login")
def login():
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
        model.postgres_session.add(new_user)
        # Process all the things and commit to the database
        model.postgres_session.commit()
        # Note that new_user is still a variable and it still has all the other info you gave it.
        # The database has more column that need to be filled in.
        # We need to ask the database for the information of the new user we have just commited. 
        # The .refresh() is like making a request to the database for the info of the new_user,
        # so that we can get the new_user.id that it has just generated to put in our user_id column in 
        # the addresses table.
        model.postgres_session.refresh(new_user)

        new_user_address = Address(user_id = new_user.id,
                                    email = email, 
                                    address1 = address1, 
                                    address2 = address2,
                                    city = city,
                                    state = state,
                                    zipcode = zipcode,
                                    country = country,
                                    phone = phone)
        # Now we've got all the stuff the database wants to put in the addresses table,
        # we can add and commit to make the addresses table.
        model.postgres_session.add(new_user_address)
        model.postgres_session.commit()
        login_user(new_user)
        
        return redirect(url_for("view_order", duck=request.args.get("duck")))

if __name__ == "__main__":
    app.run(debug=True)
