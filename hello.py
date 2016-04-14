from flask import Flask, render_template
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask.ext.moment import Moment
from datetime import datetime
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


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
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('index.html', form=form, name=name,current_time=datetime.utcnow())

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
	text = None
	pos_count = None
	neg_count = None
	form = TextForm()
	if form.validate_on_submit():
		text = form.text.data
		form.text.data = ''
		textdata = text
		pos_count,neg_count = text_mining_engine(textdata)
		
	return render_template('textmining.html', form=form,text=text, pos_count=pos_count,neg_count=neg_count,current_time=datetime.utcnow())


if __name__ == '__main__':
    manager.run()
