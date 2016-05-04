import re
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