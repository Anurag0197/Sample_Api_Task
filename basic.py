from flask import Flask,render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask import request
import os
import json
import xlrd
import statistics                  
import datetime
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')

db = SQLAlchemy(app)

class Data(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    date =  db.Column(db.String(30))
    data =  db.Column(db.Integer)


    def __init__(self,date,data):

        self.date = date
        self.data = data


@app.route('/',methods = ['GET','POST'])
def index():

    file_location = "/home/anurag/Desktop/Internship/stats/SampleData.csv"
    book = xlrd.open_workbook(file_location)                 #Setting Excel File Pointer

    sheet = book.sheet_by_index(0)

    time = []
    data = []
    x = []
    for row in range(1,sheet.nrows):
	    data.append(sheet.cell_value(row,1)) #retrieving data from excel file
	    x.append(sheet.cell_value(row,0))    #retrieving date from excel file

    for date in range(len(x)):
        time.append(xlrd.xldate_as_tuple(x[date],0))  #converting date into desired form

    temp = []
    month = []

    for i in range(len(time)):
        temp.append(datetime.datetime(*time[i]))

    for i in range(len(temp)):
        temp[i] = str(temp[i])
	  #  temp[i] = temp[i][:10]

    for i in range(len(temp)):
        temp[i] = temp[i][5:7]                   #extracting month from date

    for i in range(len(temp)):
        y = Data(temp[i],data[i])
        db.session.add(y)

    db.session.commit()

    if request.method == 'POST':
    #    if form.validate_on_submit():
            choice = request.form.get("chose")
            q = 1
            if choice == 'weekly':
                for i in range(len(temp)-1):
                	if temp[i] != temp[i+1]:          #logic of choosing month (if month has changed then I am keeping the last entry of month)
                		month.append(data[i])

                month.append(data[len(data)-1])

                frequency_weekly_mean = statistics.mean(data)
                frequency_weekly_std_dev = statistics.stdev(data)     	#finding mean, std_dev, max, min of weekly's data
                frequency_weekly_max = max(data)
                frequency_weekly_min = min(data)


                frequency_monthly_mean = statistics.mean(month)       #finding mean, std_dev, max, min of monthly's data
                frequency_monthly_std_dev = statistics.stdev(month)
                frequency_monthly_max = max(month)
                frequency_monthly_min = min(month)

                pri = []

                pri.append(frequency_weekly_mean)
                pri.append(frequency_weekly_std_dev)
                pri.append(frequency_weekly_max)
                pri.append(frequency_weekly_min)
                pri.append("weekly")
                return render_template('index.html',a=pri,q=q)

            elif choice == 'monthly':
                for i in range(len(temp)-1):
                	if temp[i] != temp[i+1]:          
                		month.append(data[i])

                month.append(data[len(data)-1])

                frequency_monthly_mean = statistics.mean(month)       
                frequency_monthly_std_dev = statistics.stdev(month)
                frequency_monthly_max = max(month)
                frequency_monthly_min = min(month)

                pri = []

                pri.append(frequency_monthly_mean)
                pri.append(frequency_monthly_std_dev)
                pri.append(frequency_monthly_max)
                pri.append(frequency_monthly_min)
                pri.append("weekly")
                return render_template('index.html',a=pri,q=q)
    else:
        q = 0
        a = ['monthly']
        return render_template('index.html',q=q,a=a)


if  __name__ == 'main':
    app.run(debug=True)
