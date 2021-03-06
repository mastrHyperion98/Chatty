import gc
import os
import json
from flask import Flask, render_template, url_for, redirect, request, session, current_app, send_from_directory, \
    send_file, flash
from flask_mail import Mail
from forms import LoginForm, CreateAccount, Settings, CreateChannelForm, RecoverPasswordForm, AddMemberForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/db.sqlite3'
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='SOEN287.CHATTY@gmail.com',
    MAIL_PASSWORD='Qwerty@321',
    MAIL_DEFAULT_SENDER='SOEN287.CHATTY@gmail.com'
)
app.secret_key = os.environ.get('SECRET_KEY') or 'DEV'
db = SQLAlchemy(app)

mail = Mail(app)
# have to import after as some imports depend on db being defined
from utils import validate_account, verify_login, find_user, login_required, update_user, add_channel, my_channels, \
    member_of, recover_password, deleteChannel, remove_member, add_member, get_channel_members, get_all_messages, \
    add_message, get_last_messages


@app.route('/')
def index():
    return redirect(url_for("login"))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if session.get('user'):
        next_page = session.get('next', url_for("dashboard"))
        session['next'] = url_for("dashboard")
        return redirect(next_page)

    form = LoginForm()
    if form.validate_on_submit():
        if verify_login(form, db):
            next_page = session.get('next', url_for("dashboard"))
            session['next'] = url_for("dashboard")
            return redirect(next_page)

    return render_template("Login.html", form=form)


@app.route('/recover', methods=['POST', 'GET'])
def recover():
    form = RecoverPasswordForm()
    if form.validate_on_submit():
        if recover_password(form, mail, db):
            return render_template("Forgot_Password.html", form=form)
    return render_template("Forgot_Password.html", form=form)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash(u"You have been logged out!", "info")
    gc.collect()
    return redirect(url_for('login'))


@app.route('/Create/Channel', methods=['POST', 'GET'])
@login_required
def create_channel():
    create_channel_form = CreateChannelForm()
    if create_channel_form.validate_on_submit():
        add_channel(create_channel_form, db)

    return render_template("CreateChannel.html", add_chanel_form=create_channel_form)


@app.route('/create-account', methods=['POST', 'GET'])
def create_account():
    form = CreateAccount()
    if form.validate_on_submit():
        if validate_account(form, db):
            return redirect(url_for("login"))
        else:
            flash(u'Username or Email already in use', 'error')
    return render_template("CreateAccount.html", form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    channel = json.loads(member_of(db))
    return render_template("Dashboard.html", channels=channel)


@app.route('/settings/account', methods=['POST', 'GET'])
@login_required
def account_settings():
    user = session['user']
    form = Settings()

    if form.validate_on_submit():
        if update_user(form, db):
            return render_template("AccountSettings.html", form=form, username=user['username'],
                                   email=user['email'],
                                   permalink=user['permalink'])
    return render_template("AccountSettings.html", form=form, username=user['username'], email=user['email'],
                           permalink=user['permalink'])


@app.route('/channels', methods=['GET'])
@login_required
def channels():
    channel = json.loads(my_channels(db))
    return render_template("Channels.html", channels=channel)


@app.route('/delete/channel/<string:permalink>', methods=['POST'])
@login_required
def delete_channel(permalink):
    if deleteChannel(db, permalink):
        return "", 200
    else:
        return '', 500


@app.route('/channels/active', methods=['GET'])
@login_required
def active_channel():
    return json.dumps({'permalink': session['channel_list']})


@app.route('/channels/members/<string:permalink>', methods=['GET'])
@login_required
def channel_members(permalink):
    members = get_channel_members(db, permalink)
    return members, 200


@app.route('/remove/member', methods=['POST'])
@login_required
def remove_channel_member():
    if remove_member(db):
        return "", 200
    else:
        return "", 405


@app.route('/add/member', methods=['POST', 'GET'])
@login_required
def add_channel_member():
    form = AddMemberForm()
    if form.validate_on_submit():
        add_member(form, db)

    return render_template('AddMember.html', form=form)


@app.route('/messages/all/<string:permalink>', methods=['GET'])
@login_required
def get_messages_all(permalink):
    messages = get_all_messages(permalink)

    return messages, 200


@app.route('/messages/add', methods=['POST'])
@login_required
def add_messages():
    content = request.json['content']
    channel_perm = request.json['permalink']
    if add_message(db, channel_perm, content):
        return "", 200
    return "", 500


@app.route('/user/username', methods=['GET'])
def get_user_username():
    if session.get('user'):
        username = session['user']['username']
        return json.dumps({'username': username}), 200

    return json.dumps({'username': 'You are not logged in'}), 200


@app.route('/download/<string:permalink>')
@login_required
def download_user_data(permalink):
    path = "Data/" + permalink + ".txt"
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run()
