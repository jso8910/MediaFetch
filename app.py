#!/Users/rosen59250/Desktop/AllCodingStuffs/APIPageFlaskWebsite/bin/python3.8

# MUST GO IN DASHBOARD.HTML: <li><a href="{{ url_for('logout') }}">Log Out</a></li>

# --------------- IMPORTS ----------------

import pygal
import os
from forms import LoginForm, RegisterForm, RevalidateForm
from flask import Flask, redirect, url_for, render_template, request, \
                jsonify, send_from_directory
import googleNewsScraper
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, \
                        logout_user, current_user
import jwt
import datetime
from functools import wraps
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_wtf.csrf import CSRFProtect
from random import choice
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
exampleQueries = ['coronavirus',
                  'cnn',
                  'fox news',
                  'zoo',
                  'iphone',
                  'android',
                  'forbes',
                  'entertainment',
                  'england',
                  'technology',
                  'bbc',
                  'google',
                  'amazon',
                  'wall street',
                  'latin america',
                  'australia',
                  'science',
                  'physics',
                  'chemistry',
                  'dow jones']

# ---------------- INIT APP -----------------

emailAddress = os.environ.get("EMAIL_ADDRESS")
secret = os.environ.get("MFS")
emailPassword = os.environ.get("MAIL_APP_PWORD")
#print(emailPassword)
#print(secret)
#print(emailAddress)

app = Flask(__name__, subdomain_matching=True)
Bootstrap(app)

app.config["SERVER_NAME"] = "localhost:5000"
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] \
= 'sqlite://///Users/rosen59250/Desktop/AllCodingStuffs/MediaFetch/database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
admin = Admin(app, template_mode='bootstrap3')

app.config['SECRET_KEY'] = secret   #SET SECRET TO ANYTHING
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = emailAddress  # EMAIL NEEDED TO SIGN UP
app.config['MAIL_PASSWORD'] = emailPassword # PASSWORD NEEDED
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

csrf = CSRFProtect(app)
csrf.init_app(app)

mail = Mail(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# ---------------- DATABASE ------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    confirmed_email = db.Column(db.Boolean)

class Calls(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user = db.Column(db.String(20), primary_key=False, unique=False)
    day = db.Column(db.String(15), unique=False)
    fullTime = db.Column(db.String(40), unique=False)
    query = db.Column(db.String(20000), unique=False)
    timeInfo = db.Column(db.String(20000), unique=False)
    excluding = db.Column(db.String(20000), unique=False)
    requiring = db.Column(db.String(20000), unique=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- DECORATOR -------------

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if request.args.get('token'):
            token = request.args.get('token')
        if not token:
            return jsonify({'status': 'error', 'error': \
                            'api token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = User.query.filter_by(
                username=data['username']).first()
            if not user:
                return jsonify({'status': 'error', 'error': 'api token is invalid'})\
                        , 401

        except:
            return jsonify({'status': 'error', 'error': 'api token is invalid'})\
                    , 401

        return f(current_user, *args, **kwargs)

    return decorated


def validated_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.confirmed_email:
            print('')
        else:
            form = RevalidateForm()
            # this is temp
            return render_template('invalidated.html', form=form)

        return f(current_user, *args, **kwargs)

    return decorated

# ----------------- ROUTES -------------

def timeList(time):
    list = time.split('-')
    for i in range(len(list)):
        list[i] = int(list[i])
    return list

@app.route('/totalGraph.svg')
def visual():
    calls = db.session.query(Calls).all()

    startStr = calls[0].__dict__['day']
    endStr = calls[len(calls) - 1].__dict__['day']

    start = timeList(startStr)
    end = timeList(endStr)

    line_chart = pygal.Line(fill=True, \
                            interpolate='cubic', \
                            style=pygal.style.DarkSolarizedStyle)
    line_chart.title = "Number of API calls per day (all users)"
    starting = datetime.date(start[0], start[1], start[2])
    ending = datetime.date(end[0], end[1], end[2])
    delta = datetime.timedelta(days=1)
    labels = []
    labels.append(str(starting - delta))
    while starting <= ending:
        labels.append(str(starting))
        starting += delta

    line_chart.x_labels = labels

    calls_per_day = {label:0 for label in labels}
    for i in range(len(labels)):
        for j in range(len(calls)):
            if calls[j].__dict__['day'] == labels[i]:
                calls_per_day[labels[i]] += 1
    line_chart.add('API Calls', [i for i in calls_per_day.values()])

    return line_chart.render(disable_xml_declaration=True, fill=True)

@app.route('/userGraph.svg')
@login_required
def visualUser():
    calls = db.session.query(Calls).all()
    for i in range(len(calls)):
        if calls[i].__dict__['user'] == current_user.username:
            startStr = calls[i].__dict__['day']
            break

    for i in range(len(calls)):
        if calls[i].__dict__['user'] == current_user.username:
            endStr = calls[i].__dict__['day']

    start = timeList(startStr)
    end = timeList(endStr)

    line_chart = pygal.Line(fill=True, \
                            interpolate='cubic', \
                            style=pygal.style.DarkSolarizedStyle)
    line_chart.title = f"Number of API calls per day (User: {current_user.username})"
    starting = datetime.date(start[0], start[1], start[2])
    ending = datetime.date(end[0], end[1], end[2])
    delta = datetime.timedelta(days=1)
    labels = []
    labels.append(str(starting - delta))
    while starting <= ending:
        labels.append(str(starting))
        starting += delta

    line_chart.x_labels = labels

    calls_per_day = {label:0 for label in labels}
    for i in range(len(labels)):
        for j in range(len(calls)):
            if calls[j].__dict__['day'] == labels[i]:
                if calls[j].__dict__['user'] == current_user.username:
                    calls_per_day[labels[i]] += 1
    line_chart.add('API Calls', [i for i in calls_per_day.values()])

    return line_chart.render(disable_xml_declaration=True, fill=True)


@app.route('/')
def homePage():
    return render_template('index.html', logged_in=not \
                            current_user.is_authenticated)


@app.route('/login/', methods=['GET', 'POST'])
# @validated_required
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return render_template('login.html', form=form, \
                                error='Invalid username or password')

    return render_template('login.html', form=form, error='')


@app.route('/regenerate_email_token/', methods=['GET', 'POST'])
# @login_required
def regen():

    form = RevalidateForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None:
            emailConfToken = s.dumps(user.email, salt='email-confirm')

            link = url_for(f'confirm_email',
                           token=emailConfToken, _external=True)

            regenUrl = url_for('regen', _external=True)

            msg = Message('Confirm Email (resent)',
                          sender='mail4jasonr@gmail.com', \
                          recipients=user.email.split())
            msg.body = f'Hello {user.username},\n\nWelcome to MediaFetch!\n\n' \
                f'Your email confirmation link is {link} and it will expire in'\
                ' 30 minutes.\n\n' \
                f'Press this link to get a new URL:\n{regenUrl}\n\nThanks for' \
                'signing up,\n The MediaFetch Team'
            mail.send(msg)

            return render_template('sent.html', logged_in=not \
                                    current_user.is_authenticated, correct=True)
        else:
            return render_template('sent.html', logged_in=not current_user\
                                    .is_authenticated, correct=False)
    return render_template('invalidated.html', form=form)


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        if User.query.filter_by(email=form.email.data).count() > 0 or \
            User.query.filter_by(email=form.username.data).count() > 0:
            return "username or email already in use"
        new_user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password, \
                        admin=False, confirmed_email=False)
        db.session.add(new_user)
        db.session.commit()
        token = jwt.encode({'username': form.username.data,
                            'email': form.email.data}, app.config['SECRET_KEY'])
        token = str(token).replace("b'", "")
        token = str(token).replace("'", "")

        emailConfToken = s.dumps(form.email.data, salt='email-confirm')

        msg = Message('Confirm Email', sender='mail4jasonr@gmail.com',
                      recipients=form.email.data.split())

        link = url_for(f'confirm_email', token=emailConfToken, _external=True)

        regenUrl = url_for('regen', _external=True)

        msg.body = f'Hello {form.username.data},\n\nWelcome to MediaFetch!\n\n'\
            f'Your email confirmation link is {link} and it will expire '\
            'in 30 minutes.\n\n' \
            f'Press this link to get a new URL:\n{regenUrl}\n\nThanks for'\
            ' signing up,\n The MediaFetch Team'

        mail.send(msg)
        return f'<h1>New user has been created. Your email \
                confirmation key is {emailConfToken}<br>Your API key \
                is </h1><p>{token}</p>'
        # TODO: MAKE THIS A PAGE FOR NEW USER

    return render_template('signup.html', form=form)
# email confirmation route


@app.route('/confirm_email/<token>/')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=30 * 60)
        # user = User.query.filter_by(username=.email)
        current_user.confirmed_email = True
        db.session.commit()
        return 'the token works!'
    except SignatureExpired:
        return 'You waited too long and your confirm email expired'
# rest of the app


@app.route('/dashboard/')
@login_required         # very important for *all* screens behind a login
@validated_required
def dashboard(current_user):
    global exampleQueries
    tokenUser = User.query.filter_by(username=current_user.username).first()
    token = jwt.encode({'username': tokenUser.username,
                        'email': tokenUser.email}, app.config['SECRET_KEY'])
    token = str(token).replace("b'", "")
    token = str(token).replace("'", "")
    return render_template('dashboard.html', name=current_user.username, \
                            token=token, query=choice(exampleQueries))

@app.route('/api')
@token_required
def api(current_user):
    query = request.args.get('query')
    timeAgo = request.args.get('time')
    excluding = request.args.get('exclude')
    requiring = request.args.get('require')
    if query is None:
        return {"status": "error",
                "error": "no query made",
                "articlesFound": 0,
                "articles": []}
    if timeAgo is None:
        timeAgo = ''
    if excluding is None:
        excluding = ''
    if requiring is None:
        requiring = ''
    token = request.args.get('token')
    time = datetime.datetime.utcnow()
    day = time.strftime('%Y-%m-%d')
    data = jwt.decode(token, app.config['SECRET_KEY'])
    call = Calls(user=data['username'], \
                 day=day, \
                 query=query, \
                 timeInfo=timeAgo, \
                 excluding=excluding, \
                 requiring=requiring, \
                 fullTime=time.ctime())
    db.session.add(call)
    db.session.commit()
    try:
        api = googleNewsScraper.searchGNews(query, timeAgo, excluding, requiring)
        return api
    except:
        data = {}
        data['status'] = 'error'
        data['error'] = 'error on the server. contact us to let us know'
        data['articlesFound'] = 0
        data['articles'] = []
        return data


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homePage'))


@app.route('/documentation/',)
def documentation():
    logged_in = not current_user.is_authenticated
    if not logged_in:
        token = jwt.encode({'username': current_user.username,
                            'email': current_user.email}, \
                            app.config['SECRET_KEY'])
        token = str(token).replace("b'", "")
        token = str(token).replace("'", "")
        return render_template('documentation.html', token=token, \
                                logged_in=logged_in)
    else:
        return render_template('documentation.html', token='TOKEN.HERE', \
                                logged_in=logged_in)


@app.route('/logo.png')
def logo():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/MediaFetch.png', \
                               mimetype='image/png')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/MediaFetch.ico', \
                               mimetype='image/vnd.microsoft.icon')

# ADMIN AND 404


class AdminModelView(ModelView):
    def is_accessible(self):

        if current_user.is_authenticated and not current_user.is_anonymous:
            user = User.query.filter_by(username=current_user.username).first()
            if user.admin:
                return True
            else:
                return False
        else:
            return False


    column_searchable_list = ['username', 'email']
    column_filters = ['admin', 'confirmed_email']
    page_size = 50

class CallsModelView(ModelView):
    def is_accessible(self):

        if current_user.is_authenticated and not current_user.is_anonymous:
            user = User.query.filter_by(username=current_user.username).first()
            if user.admin:
                return True
            else:
                return False
        else:
            return False


    column_filters = ['id']
    page_size = 50



admin.add_view(AdminModelView(User, db.session))
admin.add_view(CallsModelView(Calls, db.session))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", logged_in=not \
                            current_user.is_authenticated)


def getApp():
    return app


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
