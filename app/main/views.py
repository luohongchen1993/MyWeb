from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
from ..email import send_email
from . import main
from .forms import NameForm
from .forms import TextForm
from datetime import datetime

@main.route('/', methods=['GET', 'POST'])
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
			if current_app.config['FLASKY_ADMIN']:
				print current_app.config['FLASKY_ADMIN']
				send_email(current_app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
		else:
			session['known'] = True
		
		# try to retain the flash feature so that I don't forget how to use it
		if session['known'] == True:
			flash('Nice to see you again!!!!!')
			
		session['name'] = form.name.data
		form.name.data = ''
		return redirect(url_for('.index'))
		
    return render_template('index.html', form=form, name=session.get('name'), known = session.get('known',False),
		current_time=datetime.utcnow())
	
@main.route('/textmining', methods=['GET', 'POST'])
def textmining():
	from textmining import text_mining_engine
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
		return redirect(url_for('.textmining'))
		
	return render_template('textmining.html', form=form,text=session.get('text'), pos_count=session.get('pos'),neg_count=session.get('neg'),current_time=datetime.utcnow())
