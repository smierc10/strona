'''
pip install --upgrade python-socketio==4.6.0

pip install --upgrade python-engineio==3.13.2

pip install --upgrade Flask-SocketIO==4.3.1
'''


from flask import Flask
from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send
import logging
logger = logging.getLogger('werkzeug')


class NoParsingFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('127')

class NoParsingFilter1(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('192')
logger.addFilter(NoParsingFilter())
logger.addFilter(NoParsingFilter1())




app = Flask(__name__,static_folder='staticFiles')
app.secret_key = "1"
#app.permanent_session_lifetime = 2
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins='*')
history = []
history_reset_key = "123"

class users(db.Model):

	_id = db.Column(db.Integer, primary_key=True)
	usr = db.Column(db.String(100))
	psw = db.Column(db.String(100))
	email = db.Column(db.String(100))

	def __init__(self ,usr ,psw ,email):
		self.usr = usr
		self.psw = psw
		self.email = email


class history1(db.Model):

	_id = db.Column(db.Integer, primary_key=True)
	msg = db.Column(db.String())

	def __init__(self ,msg):
		self.msg = msg


@socketio.on('message')
def handleMessage(msg):
	global history
	print('Message: ' + msg)
	send(msg, broadcast=True)
	if not msg.endswith('has connected!'): 
		history.append(msg)
	if msg == history_reset_key:
		history = []

@socketio.on('requestforhistory')
def sendhistory():
	for i in range(len(history)):
		send(history[i])
		



@app.route('/chat')
def chat():
	if "username" in session and "password" in session:
		us = session["username"]
		return render_template('chat.html',us=us)
	else:
		return redirect(url_for('login'))


@app.route('/delete')
def delete():
	users.query.delete()
	return "usunieto pomyślnie"

@app.route('/deletehistory')
def delete2():
	global history
	history = []
	return "usunieto historie pomyślnie"



@app.route("/login" , methods = ['POST','GET'])
def login():
	if request.method == "POST":
		
		us = request.form['us']
		ps = request.form['ps']
		#usr_data = users(usr=us,psw=ps,email=email)
		#db.session.add(usr_data)
		#db.session.commit()
		found_user = users.query.filter_by(usr=us).first()
		if found_user and found_user.psw == ps:
			session["username"] = us
			session["password"] = ps
			session["email"] = found_user.email
			return redirect(url_for('home'))
		elif found_user:
			return "niepoprawne hasło"
		else:
			return "wypelnij rubryke hasła i nazwy"
	else:
		if "username" in session and "password" in session:
			return redirect(url_for('jd'))
		else:
			return render_template("login.html")

@app.route('/user', methods = ['POST','GET'])
def user():
	username = session["username"]
	found_user = users.query.filter_by(usr=username).first()
	if request.method == 'POST':
		email = request.form['email']
		found_user.email = email
		db.session.commit()
		return redirect(url_for('user'))
	else:
		
		email = "email"
		if found_user.email != '':
			email = found_user.email
			session["email"] = email
		return render_template('user.html',email=email,username=username)

@app.route('/logout')
def logout():
	session.pop("username",None)
	session.pop("password",None)
	return redirect(url_for('home'))


@app.route('/register', methods=['POST','GET'])
def register():
	if request.method == 'POST':
		us = request.form['us']
		ps = request.form['ps']
		email = request.form['email']
		found_user = users.query.filter_by(usr=us).first()
		if ps and us:
			if not found_user:
				usr_data = users(usr=us,psw=ps,email=email)
				db.session.add(usr_data)
				db.session.commit()
				session["username"] = us
				session["password"] = ps
				if email != None:
					session["email"] = email
				return redirect(url_for('home'))
			else:
				return "przykro mi taki uzytwkonik juz istnieje"
		else:
			return "aby stworzyc konto trzeba podac nazwe i haslo"
	else:
		return render_template('login.html')


@app.route('/')
def home():
	user = ""
	if "username" in session:
		user = session["username"]
	return render_template('home.html',username=user)


if __name__ == '__main__':
	db.create_all()
	socketio.run(app,debug=True,host='0.0.0.0',port=5000)

