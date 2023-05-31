from sys import _current_frames
from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory

import os
import openai
from dotenv import load_dotenv
import json
import pprint
import PyPDF2
import pandas as pd 
load_dotenv()


from werkzeug.utils import secure_filename

UPLOAD_FOLDER = r'C:\Users\bhara\py\resume_to_structured_data_flask\\'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
file_nam = ''



app = Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER



@app.route('/', methods=['GET','POST'])
def he():
    return render_template("index.html")


@app.route('/data', methods=['GET','POST'])
def home():
    global file_nam
    path = UPLOAD_FOLDER+file_nam
    pdfFileObj = open(path, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    text = ''
    for x in range(pdfReader.numPages) :
        pageObj = pdfReader.getPage(x)
        text += pageObj.extract_text()
    print(text)
    pdfFileObj.close()
 

    openai.api_key = os.getenv("OPENAI_API_KEY")
    finalPrompt = "We have information about the academic information of a person\n\n" + text + "\n\nAnswer the below questions in a JSON file.\n\nName?\nShort Description or Profile or Summary?\nEducation with years studied, Degree and College?\nSkills?\nContact Number?\nEmail?\nAddress?\nHobbies?\nJob Experience or Employment History?\nYears of Experience?\nAccomplishments?\n\n"
    print(finalPrompt)
    response = openai.Completion.create(
    model="text-davinci-002",
    prompt=finalPrompt,
    temperature=0,
    max_tokens=1000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )


    answer = response.choices[0].text
    # print('...')
    j = json.loads(answer)
    

    l=list(j.values())
    # print(l)


    # file = open("resume.csv", "a")
    # file.write("\n")
    # for i in range(0,len(l)):
    #     file.write("\"")
    #     file.write(str(l[i]))
    #     file.write("\"")
    #     if(i<len(l)-1):
    #         file.write(",")


    # file.close()
    return render_template('home1.html',data=j)



@app.route('/query', methods=['GET','POST'])
def qer():
    answer = ''
    if request.method == 'POST':
        # pdf = request.form["person"]
        question = request.form["question"]
        global file_nam
        path = UPLOAD_FOLDER+file_nam
        pdfFileObj = open(path, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        text = ''
        for x in range(pdfReader.numPages) :
            pageObj = pdfReader.getPage(x)
            text += pageObj.extract_text()
        print(text)
        pdfFileObj.close()

        openai.api_key = os.getenv("OPENAI_API_KEY")
        finalPrompt = "We have information about the academic information of a person\n\n" + text + "\n\nAnswer the following question given below\n\n"+ question + "\n\n"
        print(finalPrompt)
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=finalPrompt + "\n\n",
            temperature=0,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )


        answer = response.choices[0].text
    return render_template("query.html", ans = answer)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/drive', methods=['GET', 'POST'])
def upload_file():
    global file_nam
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(filename)
            file_nam = filename
            
            return render_template('query.html', file=filename)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)






if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)