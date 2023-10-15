import flask
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_required, logout_user, login_user
from uuid import uuid4
from datetime import datetime

app = flask.Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "sjSVe-sgah33-qg41a"

db = SQLAlchemy(app=app)


class AvailableApp(db.Model):
    id = db.Column(db.String, primary_key=True)
    app_name = db.Column(db.String)
    app_file_name = db.Column(db.String)
    app_icon_name = db.Column(db.String)
    app_category = db.Column(db.String)


class AppReview(db.Model):
    id = db.Column(db.String, primary_key=True)
    business_fk = db.Column(db.String)
    point = db.Column(db.Integer)
    app_fk = db.Column(db.String)


class Business(db.Model):
    id = db.Column(db.String, primary_key=True)
    business_name = db.Column(db.String)
    business_domain = db.Column(db.String)


class CardInformation(db.Model):
    id = db.Column(db.String, primary_key=True)
    card_number = db.Column(db.Integer)
    expiration_date = db.Column(db.String)
    cvv = db.Column(db.Integer)
    cardholder_name = db.Column(db.String)
    postal_code = db.Column(db.String)
    country_registered = db.Column(db.String)


class BusinessUserProfile(db.Model):
    id = db.Column(db.String, primary_key=True)
    business_email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    business_fk = db.Column(db.String)
    access_level = db.Column(db.Integer)


class DeveloperAccount(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_fk = db.Column(db.String)
    developer_status = db.Column(db.String, default="Not Approved")
    account_balance = db.Column(db.String)


class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    registration_date = db.Column(db.Date)


def install_app(user_code=None, installer_user=None):
    app_to_install = AvailableApp.query.get(user_code)
    installer_b = BusinessUserProfile.query.get(installer_user)
    files = {
        'archive': open(f"available_apps/{app_to_install.app_file_name}.zip", "rb"),
        "app_icon": open(f"app_icons/{app_to_install.app_icon_name}", "rb")
    }
    data = {
        "app_name": app_to_install.app_name
    }
    business_information = Business.query.get(installer_b.business_fk)
    url = business_information.business_domain

    requests.post(url=url, files=files, data=data)

# https://apps.microsoft.com/store/apps use microsoft store as an example while building the store for modular


@app.route("/store")
def store():
    installable_apps = [
        {
            "app_name": app_filter,
            "star_count": int(sum([i for i in AppReview.query.filter_by(app_fk=app_filter.id).all()])),
            "app_id": app_filter.id,
            "app_category": app_filter.app_category,
            "app_image": app_filter.app_icon_name
        }
        for app_filter in AvailableApp.query.all()
    ]
    return flask.render_template("store.html", installable_apps=installable_apps)


@app.route("/signin")
def sign_in():
    return flask.render_template("signin.html")


@app.route("/view-emails")
def view_emails():
    return flask.jsonify(list(set([i.email for i in User.query.all()])))


@app.route("/card-information", methods=["POST", "GET"])
def card_information():
    if flask.request.method == "POST":
        values = flask.request.values
        new_card_data = CardInformation(card_number=values["cc"], expiration_date=values["expiration_date"],
                                        cvv=values["cvv"], cardholder_name=values["cardholder-name"],
                                        postal_code=values["cardholder-postalcode"])
        db.session.add(new_card_data)
        db.session.commit()

        return '''
            <script>
                alert('Successfully saved your card!')
                document.location = '/'
            </script>
        '''
    return flask.render_template("card-info.html")


@app.route("/", methods=["POST", "GET"])
def index():
    if flask.request.method == "POST":
        new_user = User(id=str(uuid4()), email=flask.request.values["email"], password=str(uuid4()),
                        registration_date=datetime.now())
        db.session.add(new_user)
        db.session.commit()
        return flask.redirect("/thanks")

    return flask.render_template("index.html")


@app.route("/thanks")
def thanks():
    return flask.render_template("thanks_for_preregister.html")


@app.route("/mobile", methods=["POST", "GET"])
def index_mobile_temp():
    if flask.request.method == "POST":
        new_user = User(id=str(uuid4()), email=flask.request.values["email"], password=str(uuid4()),
                        registration_date=datetime.now())
        db.session.add(new_user)
        db.session.commit()
        return flask.render_template("thanks_for_preregister.html")

    return flask.render_template("mobile-temp-index.html")


@app.route("/static/image_name")
def static_host(image_name):
    return flask.send_file("static/" + image_name)


@app.route("/app_icons/<icon_name>")
def app_icons(icon_name):
    return flask.send_file("app_icons/" + icon_name)
