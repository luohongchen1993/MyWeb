from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required



class NameForm(Form):
    name = StringField('What is your favorite movie?', validators=[Required()])
    submit = SubmitField('Submit')
	
class TextForm(Form):
	text = StringField('What is the text you wanna analyze?', validators = [Required()])
	submit = SubmitField('Submit')