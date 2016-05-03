from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask.ext.moment import Moment
from datetime import datetime
import re
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.script import Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.mail import Mail
from flask.ext.mail import Message
import pdb
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <luohongchenapp@gmail.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')



manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)



class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)

	def __repr__(self):
		return '<Role %r>' % self.name

	users = db.relationship('User', backref='role', lazy='dynamic')

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)

	def __repr__(self):
		return '<User %r>' % self.username
		
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)
# send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
		sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	# mail.send(msg)
	thr = Thread(target=send_async_email, args=[app, msg])
	thr.start()
	return thr



class NameForm(Form):
    name = StringField('What is your favorite movie?', validators=[Required()])
    submit = SubmitField('Submit')
	
class TextForm(Form):
	text = StringField('What is the text you wanna analyze?', validators = [Required()])
	submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    # name = None    # now we don't need this
    form = NameForm()
    if form.validate_on_submit():
        # 4a
		# session['name'] = form.name.data 
        # return redirect(url_for('index'))
		# old_name = session.get('name') # might be None
		
		# 5b, added database
		
		# first check if this user exist in database
		user = User.query.filter_by(username=form.name.data).first() 
		
		# if user did not exist, create 
		if user is None: 
			user = User(username = form.name.data)
			db.session.add(user)
			# db.session.commit()?
			session['known'] = False
			if app.config['FLASKY_ADMIN']:
				print app.config['FLASKY_ADMIN']
				send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
		else:
			session['known'] = True
		
		# try to retain the flash feature so that I don't forget how to use it
		if session['known'] == True:
			flash('Nice to see you again!!!!!')
			
		session['name'] = form.name.data
		form.name.data = ''
		return redirect(url_for('index'))
		
    return render_template('index.html', form=form, name=session.get('name'), known = session.get('known',False),
		current_time=datetime.utcnow())

def text_mining_engine(textdata):
	positive = ['love', 'like', 'enjoy', 'good', 'happy', 'great', 'wonderful', 'terrific', 'cool', 'best']
	negative = ['bad', 'worst', 'sad', 'unhappy', 'unpleasant', 'hate', 'angry', 'awful', 'poor','annoying']
	textdata = ' """'+textdata+ '""" '
	textdata = re.sub('[^a-zA-Z]',' ',textdata)
	textdata = textdata.lower()
	textdata_array = textdata.split(' ')

	pos_count = 0
	neg_count = 0

	for i in textdata_array:
		if i in positive:
			pos_count+=1
		
		elif i in negative:
			neg_count+=1
			
	return pos_count,neg_count
	
@app.route('/textmining', methods=['GET', 'POST'])
def textmining():
	#text = None
	#pos_count = None
	#neg_count = None
	form = TextForm()
	if form.validate_on_submit():
		#text = form.text.data
		#form.text.data = ''
		oldtext = session.get('text')
		if oldtext is not None and oldtext != form.text.data:
			flash('We are now analyzing new text data!')
		textdata = form.text.data
		pos_count,neg_count = text_mining_engine(textdata)
		session['text'] = form.text.data
		session['pos'] = pos_count
		session['neg'] = neg_count
		form.text.data = ''
		return redirect(url_for('textmining'))
		
	return render_template('textmining.html', form=form,text=session.get('text'), pos_count=session.get('pos'),neg_count=session.get('neg'),current_time=datetime.utcnow())

def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
