from flask import Flask,render_template,url_for,redirect,request
import Text_summarization
from werkzeug.utils import secure_filename
from allennlp.predictors.predictor import Predictor
from summarizer import Summarizer
import os

application=app=Flask(__name__)
app.config['UPLOAD_FOLDER']= 'uploads/'

text=''
text_summary=''

predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bidaf-model-2020.03.19.tar.gz")


@app.route('/',methods=["GET","POST"])
def dashboard():
    return render_template('index.html')



def readfile(flag):
	global text
	global text_summary
	File=''

	#loads file from 
	if(flag==0):
		File=request.files['filename']
	else:
		File=request.files['file_summary']

	#contains filename
	fn=os.path.basename(File.filename)

	#saving file in specified directory
	File.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(File.filename)))

	#contains path where file is saved
	File=str(os.path.join(app.config['UPLOAD_FOLDER'])+fn)

	#dividing the file location into its filename and extension
	name, ext =os.path.splitext(File)

	#checking whether the file is videofile or not 
	allowed_extensions=[".doc",".docx",".odt",".pdf",".rtf",".tex",".txt",".wpd"]
	if (ext.lower() in allowed_extensions)==False:
		return "extension_error"

	# flag=0 -> Original_File
	# flag=1 -> Summary_File
	if(flag==0):
		try:
			f = open(File, "r")
			text =f.read()
			return "successfully_read"
		except Exception:
			return "Something_went_wrong"

	else:
		try:
			f = open(File, "r")
			text_summary =f.read()
			return "successfully_read"
		except Exception:
			return "Something_went_wrong"



@app.route('/summarize',methods=["GET","POST"])
def summarize():
	if request.method=="POST":
		radio_butt=request.form.get("optradio")
		print(radio_butt)
		output=readfile(0)
		if(output=="extension_error"):
			return render_template("summarize.html",summary_output="Not a text file")

		if(output=="Something_went_wrong"):
			return render_template("summarize.html",summary_output="Sorry!!! Something_went_wrong")

		if(radio_butt=="bert"):
			model = Summarizer()
			pred_summary = model(text)
			return render_template("summarize.html",summary_output=pred_summary)
		else:
			pred_summary=Text_summarization.get_data(text,'',0)
			return render_template("summarize.html",summary_output=pred_summary)
			
	return render_template('summarize.html')



@app.route('/analyse',methods=["GET","POST"])
def analyse():
	global text
	global text_summary
	if request.method=="POST":

		output_text=readfile(0)
		output_summary=readfile(1)

		#if original file is not a text file
		if(output_text=="extension_error"):
			return render_template("analyse.html",analyse_output="Original file is not a text file")

		if(output_summary=="extension_error"):
			return render_template("analyse.html",analyse_output="summary file is not a text file")

		if(output_text=="Something_went_wrong" or output_summary=="Something_went_wrong"):
			return render_template("analyse.html",analyse_output="Sorry!!! Something_went_wrong")
		
		accuracy=Text_summarization.get_data(text,text_summary,1)
		return render_template("analyse.html",analyse_output=accuracy)

	return render_template('analyse.html')



@app.route('/quesans',methods=["GET","POST"])
def quesans():
	return render_template('quesans.html')



@app.route('/file',methods=["POST"])
def file():
	global text

	output=readfile(0)

	if(output=="extension_error"):
		return render_template("quesans.html",qa_output="Not a text file")

	if(output=="successfully_read"):
		return render_template("quesans.html",qa_output="File uploaded successfully")

	if(output=="Something_went_wrong"):
		return render_template("quesans.html",qa_output="Sorry!!! Something_went_wrong")



@app.route('/question',methods=["GET","POST"])
def question():
	global text
	question=str(request.form.get('comment'))
	try:
		result=predictor.predict(
		  	passage=text,
	        question=question
		)
		answer=result['best_span_str']
		return render_template("quesans.html",answer=answer)
	except Exception:
		return render_template("quesans.html",answer="Sorry!!! Currently application is out of service")



if __name__=="__main__":
	app.run()
