from flask import Flask,render_template, request
import json
import xlrd
import statistics
import datetime
from .model import *
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from scipy.stats import pearsonr

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

@app.route('/add/data/database')
def add():

    file_location1 = "/home/anurag/testing_weekly2.xlsx"

    book1 = xlrd.open_workbook(file_location1)

    sheet1 = book1.sheet_by_index(0)

    frequeny = []
    refer_id = []

    for row in range(1,sheet1.nrows):
        frequeny.append(sheet1.cell_value(row,3))
        refer_id.append(sheet1.cell_value(row,0))

    for i in range(len(frequeny)):
        y = Index(frequeny[i],refer_id[i])
        db.session.add(y)

    db.session.commit()

    file_location2 = "/home/anurag/testing_weekly.xlsx"

    book2 = xlrd.open_workbook(file_location2)

    sheet2 = book2.sheet_by_index(0)

    date = []
    data = []
    time = []
    temp = []
    refer_foreign_id = []
    foreign_id = []

    for row in range(1,sheet2.nrows):
        date.append(sheet2.cell_value(row,20))
        data.append(sheet2.cell_value(row,21))
        refer_foreign_id.append(sheet2.cell_value(row,10))

    for i in range(len(date)):
    	time.append(xlrd.xldate_as_tuple(date[i],0))  #converting date into desired form

    temp = []

    for i in range(len(time)):
    	temp.append(datetime.datetime(*time[i]))

    for i in range(len(temp)):
        temp[i] = str(temp[i])
        temp[i] = temp[i][:10]

    for i in range(len(temp)):
        date[i] = temp[i]

    for i in range(len(refer_foreign_id)):
        t = refer_foreign_id[i]
        r = Index.query.filter_by(refer_id=t).first()
        foreign_id.append(r.id)

    for i in range(len(date)):
        temp1 = Data(date[i],data[i],foreign_id[i],refer_foreign_id[i])
        db.session.add(temp1)

    db.session.commit()

    return render_template('add.html')

@app.route('/add',methods = ['GET','POST'])
def index():
    a = request.args.get("id")
    x = []
    ids = []
    q = 1
    c = a.find(',')

    if c == -1:
        ids.append(int(a[1:len(a)-1]))

    else:
        for i in range(len(a)):
            if a[i] == ',':
                x.append(i)
        b = 1
        for i in range(len(x)):
            ids.append(int(a[b:x[i]]))
            b = x[i]+1
        i = len(a)-1
        ids.append(int(a[x[-1]+1:i]))

    frequencies = []
    object = []
    datas = []
    dates = []

    for i in range(len(ids)):
        f = Index.query.filter_by(id=ids[i]).first()
        frequencies.append(f.frequency)
        object.append(f)

    if request.method == 'POST':
        choice = []
        for i in range(len(frequencies)):
            choice.append(request.form.get(str(i)))

        weekly_mean = []
        monthly_mean = []
        quarterly_mean = []
        yearly_mean = []
        weekly_std_dev = []
        monthly_std_dev = []
        quarterly_std_dev = []
        yearly_std_dev = []
        weekly_max = []
        monthly_max = []
        quarterly_max = []
        yearly_max = []
        weekly_min = []
        monthly_min = []
        quarterly_min = []
        yearly_min = []
        data_send  = []
        sums = []

        for i in range(len(choice)):

            datas.clear()
            dates.clear()


            if choice[i] != "None": #else:
                l = object[i].ref_data.all()

                if len(l) != 0:
                    for k in range(len(l)):
                        datas.append(l[k].data)
                        dates.append(l[k].date)

                    if frequencies[i] == 'Daily' or frequencies[i] == 'daily':


                        week = []
                        weekly_data1 = []
                        weekly_data2 = []

                        for k in range(len(dates)):
                            week.append(dates[k][8:10])


                        count = 0
                        for k in range(len(week)):
                            count += 1
                            if count == 7:
                                weekly_data1.append(datas[k])
                                count = 0


                        count = 0
                        t = []
                        for k in range(len(week)):
                            count += 1
                            t.append(datas[k])

                            if count == 7:
                                weekly_data2.append(statistics.mean(t))
                                count = 0
                                t.clear()

                        t.clear()

                        month = []
                        monthly_data1 = []
                        monthly_data2 = []

                        for k in range(len(dates)):
                        	c = dates[k]
                        	month.append(c[5:7])

                        for k in range(len(month)) :
                        	month[k] = int(month[k])

                        for k in range(len(month)-1):
                        	if month[k] != month[k+1]:
                        		monthly_data1.append(datas[k])

                        monthly_data1.append(datas[-1])

                        flag = 0
                        for k in range(len(month)-1):

                            if month[k] == month[k+1]:
                                flag = 1
                                t.append(datas[k])

                            elif month[k] != month[k+1]:
                                flag = -1
                                t.append(datas[k])
                                monthly_data2.append(statistics.mean(t))
                                t.clear()

                        if flag == 1:
                            t.append(datas[-1])
                            monthly_data2.append(statistics.mean(t))
                            t.clear()

                        else:
                            monthly_data2.append(datas[-1])
                            t.clear()

                        t.clear()

                        quaterly_data1 = []
                        quaterly_data2 = []

#                        b = month[0]

                        for k in range(len(month)-1):
                            if month[k] == 3 and month[k+1] != 3:
                                quaterly_data1.append(datas[k])

                            elif month[k] == 6 and month[k+1] != 6:
                                quaterly_data1.append(datas[k])

                            elif month[k] == 9 and month[k+1] != 9:
                                quaterly_data1.append(datas[k])

                            elif month[k] == 12 and month[k+1] != 12:
                                quaterly_data1.append(datas[k])

                        if month[-1] == 3 or month[-1] == 6 or month[-1] == 9 or month[-1] == 12:
                            quaterly_data1.append(datas[-1])


                        p = 0
                        for k in range(len(month)-1):
                            if month[k] == 3 and month[k+1] != 3:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                            elif month[k] == 6 and month[k+1] != 6:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                            elif month[k] == 9 and month[k+1] != 9:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                            elif month[k] == 12 and month[k+1] != 12:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                        if month[-1] == 3 or month[-1] == 6 or month[-1] == 9 or month[-1] == 12:
                            if month[-1] != month[-2]:
                                quaterly_data2.append(datas[-1])
                            else:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                        t.clear()
                        yearly_data1 = []
                        yearly_data2 = []
                        year = []

                        for k in range(len(dates)):
                        	year.append(dates[k][0:4])

                        for k in range(len(year)-1):
                        	if year[k] != year[k+1]:
                        		yearly_data1.append(datas[k])

                        yearly_data1.append(datas[len(datas)-1])

                        flag = 0
                        for k in range(len(year)-1):
                            if year[k] == year[k+1]:
                                flag = 1
                                t.append(datas[k])


                            elif year[k] != year[k+1]:
                                flag = -1
                                t.append(datas[k])
                                yearly_data2.append(statistics.mean(t))
                                t.clear()

                        if flag == 1:
                            t.append(datas[-1])
                            yearly_data2.append(statistics.mean(t))
                            t.clear()

                        else:
                            yearly_data2.append(datas[-1])
                            t.clear()

                        t.clear()

                        frequency_weekly_mean1 = statistics.mean(weekly_data1)
                        frequency_weekly_mean2 = statistics.mean(weekly_data2)
                        frequency_weekly_std_dev1 = statistics.stdev(weekly_data1)
                        frequency_weekly_std_dev2 = statistics.stdev(weekly_data2)
                        frequency_weekly_max1 = max(weekly_data1)
                        frequency_weekly_max2 = max(weekly_data2)
                        frequency_weekly_min1 = max(weekly_data1)
                        frequency_weekly_min2 = min(weekly_data2)
                        sum_weekly_1 = sum(weekly_data1)
                        sum_weekly_2 = sum(weekly_data2)


                        frequency_monthly_mean1 = statistics.mean(monthly_data1)
                        frequency_monthly_mean2 = statistics.mean(monthly_data2)
                        frequency_monthly_std_dev1 = statistics.stdev(monthly_data1)
                        frequency_monthly_std_dev2 = statistics.stdev(monthly_data2)
                        frequency_monthly_max1 = max(monthly_data1)
                        frequency_monthly_max2 = max(monthly_data2)
                        frequency_monthly_min1 = max(monthly_data1)
                        frequency_monthly_min2 = min(monthly_data2)
                        sum_monthly_1 = sum(monthly_data1)
                        sum_monthly_2 = sum(monthly_data2)


                        frequency_quaterly_mean1 = statistics.mean(quaterly_data1)
                        frequency_quaterly_mean2 = statistics.mean(quaterly_data2)
                        frequency_quaterly_std_dev1 = statistics.stdev(quaterly_data1)
                        frequency_quaterly_std_dev2 = statistics.stdev(quaterly_data2)
                        frequency_quaterly_max1 = max(quaterly_data1)
                        frequency_quaterly_max2 = max(quaterly_data2)
                        frequency_quaterly_min1 = max(quaterly_data1)
                        frequency_quaterly_min2 = min(quaterly_data2)
                        sum_quaterly_1 = sum(quaterly_data1)
                        sum_quaterly_2 = sum(quaterly_data2)

                        frequency_yearly_mean1 = statistics.mean(yearly_data1)
                        frequency_yearly_mean2 = statistics.mean(yearly_data2)
                        frequency_yearly_std_dev1 = statistics.stdev(yearly_data1)
                        frequency_yearly_std_dev2 = statistics.stdev(yearly_data2)
                        frequency_yearly_max1 = max(yearly_data1)
                        frequency_yearly_max2 = max(yearly_data2)
                        frequency_yearly_min1 = max(yearly_data1)
                        frequency_yearly_min2 = min(yearly_data2)
                        sum_yearly_1 = sum(yearly_data1)
                        sum_yearly_2 = sum(yearly_data2)

                        weekly_mean.append(frequency_weekly_mean1)
                        weekly_mean.append(frequency_weekly_mean2)
                        weekly_std_dev.append(frequency_weekly_std_dev1)
                        weekly_std_dev.append(frequency_weekly_std_dev2)
                        weekly_max.append(frequency_weekly_max1)
                        weekly_max.append(frequency_weekly_max2)
                        weekly_min.append(frequency_weekly_min1)
                        weekly_min.append(frequency_weekly_min2)

                        monthly_mean.append(frequency_monthly_mean1)
                        monthly_mean.append(frequency_monthly_mean2)
                        monthly_std_dev.append(frequency_monthly_std_dev1)
                        monthly_std_dev.append(frequency_monthly_std_dev2)
                        monthly_max.append(frequency_monthly_max1)
                        monthly_max.append(frequency_monthly_max2)
                        monthly_min.append(frequency_monthly_min1)
                        monthly_min.append(frequency_monthly_min2)

                        quarterly_mean.append(frequency_quaterly_mean1)
                        quarterly_mean.append(frequency_quaterly_mean2)
                        quarterly_std_dev.append(frequency_quaterly_std_dev1)
                        quarterly_std_dev.append(frequency_quaterly_std_dev2)
                        quarterly_max.append(frequency_quaterly_max1)
                        quarterly_max.append(frequency_quaterly_max2)
                        quarterly_min.append(frequency_quaterly_min1)
                        quarterly_min.append(frequency_quaterly_min2)

                        yearly_mean.append(frequency_yearly_mean1)
                        yearly_mean.append(frequency_yearly_mean2)
                        yearly_std_dev.append(frequency_yearly_std_dev1)
                        yearly_std_dev.append(frequency_yearly_std_dev2)
                        yearly_max.append(frequency_yearly_max1)
                        yearly_max.append(frequency_yearly_max2)
                        yearly_min.append(frequency_yearly_min1)
                        yearly_min.append(frequency_yearly_min2)

                        if choice[i] == 'Weekly' or choice[i] == 'weekly':
                            data_send.append(weekly_mean[-1])
                            data_send.append(weekly_mean[-2])
                            data_send.append(weekly_std_dev[-1])
                            data_send.append(weekly_std_dev[-2])
                            data_send.append(weekly_max[-1])
                            data_send.append(weekly_max[-2])
                            data_send.append(weekly_min[-1])
                            data_send.append(weekly_min[-2])
                            sums.append(sum_weekly_1)
                            sums.append(sum_weekly_2)

                        elif choice[i] == 'Monthly' or choice[i] == 'monthly':

                            data_send.append(monthly_mean[-1])
                            data_send.append(monthly_mean[-2])
                            data_send.append(monthly_std_dev[-1])
                            data_send.append(monthly_std_dev[-2])
                            data_send.append(monthly_max[-1])
                            data_send.append(monthly_max[-2])
                            data_send.append(monthly_min[-1])
                            data_send.append(monthly_min[-2])
                            sums.append(sum_monthly_1)
                            sums.append(sum_monthly_2)

                        elif choice[i] == 'Quarterly' or choice[i] == 'quarterly':
                            data_send.append(quarterly_mean[-1])
                            data_send.append(quarterly_mean[-2])
                            data_send.append(quarterly_std_dev[-1])
                            data_send.append(quarterly_std_dev[-2])
                            data_send.append(quarterly_max[-1])
                            data_send.append(quarterly_max[-2])
                            data_send.append(quarterly_min[-1])
                            data_send.append(quarterly_min[-2])
                            sums.append(sum_quaterly_1)
                            sums.append(sum_quaterly_2)

                        elif choice[i] == 'Yearly' or choice[i] == 'yearly':

                            data_send.append(yearly_mean[-1])
                            data_send.append(yearly_mean[-2])
                            data_send.append(yearly_std_dev[-1])
                            data_send.append(yearly_std_dev[-2])
                            data_send.append(yearly_max[-1])
                            data_send.append(yearly_max[-2])
                            data_send.append(yearly_min[-1])
                            data_send.append(yearly_max[-2])
                            sums.append(sum_yearly_1)
                            sums.append(sum_yearly_2)

                    elif frequencies[i] == 'Weekly' or frequencies[i] == 'weekly':

                        t = []

                        month = []
                        monthly_data1 = []
                        monthly_data2 = []


                        for k in range(len(dates)):
                        	c = dates[k]
                        	month.append(c[5:7])

                        for k in range(len(month)) :
                        	month[k] = int(month[k])

                        for k in range(len(month)-1):
                        	if month[k] != month[k+1]:
                        		monthly_data1.append(datas[k])

                        monthly_data1.append(datas[-1])

                        flag = 0
                        for k in range(len(month)-1):

                            if month[k] == month[k+1]:
                                flag = 1
                                t.append(datas[k])

                            elif month[k] != month[k+1]:
                                flag = -1
                                t.append(datas[k])
                                monthly_data2.append(statistics.mean(t))
                                t.clear()

                        if flag == 1:
                            t.append(datas[-1])
                            monthly_data2.append(statistics.mean(t))
                            t.clear()

                        else:
                            monthly_data2.append(datas[-1])
                            t.clear()

                        t.clear()

                        quaterly_data1 = []
                        quaterly_data2 = []

                        for k in range(len(month)-1):
                            if month[k] == 3 and month[k+1] != 3:
                                quaterly_data1.append(datas[k])

                            elif month[k] == 6 and month[k+1] != 6:
                                quaterly_data1.append(datas[k])

                            elif month[k] == 9 and month[k+1] != 9:
                                quaterly_data1.append(datas[k])

                            elif month[k] == 12 and month[k+1] != 12:
                                quaterly_data1.append(datas[k])

                        if month[-1] == 3 or month[-1] == 6 or month[-1] == 9 or month[-1] == 12:
                            quaterly_data1.append(datas[-1])

                        p = 0
                        for k in range(len(month)-1):
                            if month[k] == 3 and month[k+1] != 3:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                            elif month[k] == 6 and month[k+1] != 6:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                            elif month[k] == 9 and month[k+1] != 9:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                            elif month[k] == 12 and month[k+1] != 12:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                        if month[-1] == 3 or month[-1] == 6 or month[-1] == 9 or month[-1] == 12:
                            if month[-1] != month[-2]:
                                quaterly_data2.append(datas[-1])
                            else:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))



                        t.clear()


                        yearly_data1 = []
                        yearly_data2 = []
                        year = []

                        for k in range(len(dates)):
                        	year.append(dates[k][0:4])

                        for k in range(len(year)-1):
                        	if year[k] != year[k+1]:
                        		yearly_data1.append(datas[k])

                        yearly_data1.append(datas[len(datas)-1])

                        flag = 0
                        for k in range(len(year)-1):
                            if year[k] == year[k+1]:
                                flag = 1
                                t.append(datas[k])

                            elif year[k] != year[k+1]:
                                flag = -1
                                t.append(datas[k])
                                yearly_data2.append(statistics.mean(t))
                                t.clear()

                        if flag == 1:
                            t.append(datas[-1])
                            yearly_data2.append(statistics.mean(t))
                            t.clear()

                        else:
                            yearly_data2.append(datas[-1])
                            t.clear()

                        t.clear()


                        frequency_monthly_mean1 = statistics.mean(monthly_data1)
                        frequency_monthly_mean2 = statistics.mean(monthly_data2)
                        frequency_monthly_std_dev1 = statistics.stdev(monthly_data1)
                        frequency_monthly_std_dev2 = statistics.stdev(monthly_data2)
                        frequency_monthly_max1 = max(monthly_data1)
                        frequency_monthly_max2 = max(monthly_data2)
                        frequency_monthly_min1 = max(monthly_data1)
                        frequency_monthly_min2 = min(monthly_data2)
                        sum_monthly_1 = sum(monthly_data1)
                        sum_monthly_2 = sum(monthly_data2)

                        frequency_quaterly_mean1 = statistics.mean(quaterly_data1)
                        frequency_quaterly_mean2 = statistics.mean(quaterly_data2)
                        frequency_quaterly_std_dev1 = statistics.stdev(quaterly_data1)
                        frequency_quaterly_std_dev2 = statistics.stdev(quaterly_data2)
                        frequency_quaterly_max1 = max(quaterly_data1)
                        frequency_quaterly_max2 = max(quaterly_data2)
                        frequency_quaterly_min1 = max(quaterly_data1)
                        frequency_quaterly_min2 = min(quaterly_data2)
                        sum_quaterly_1 = sum(quaterly_data1)
                        sum_quaterly_2 = sum(quaterly_data2)

                        frequency_yearly_mean1 = statistics.mean(yearly_data1)
                        frequency_yearly_mean2 = statistics.mean(yearly_data2)
                        frequency_yearly_std_dev1 = statistics.stdev(yearly_data1)
                        frequency_yearly_std_dev2 = statistics.stdev(yearly_data2)
                        frequency_yearly_max1 = max(yearly_data1)
                        frequency_yearly_max2 = max(yearly_data2)
                        frequency_yearly_min1 = max(yearly_data1)
                        frequency_yearly_min2 = min(yearly_data2)
                        sum_yearly_1 = sum(yearly_data1)
                        sum_yearly_2 = sum(yearly_data2)

                        monthly_mean.append(frequency_monthly_mean1)
                        monthly_mean.append(frequency_monthly_mean2)
                        monthly_std_dev.append(frequency_monthly_std_dev1)
                        monthly_std_dev.append(frequency_monthly_std_dev2)
                        monthly_max.append(frequency_monthly_max1)
                        monthly_max.append(frequency_monthly_max2)
                        monthly_min.append(frequency_monthly_min1)
                        monthly_min.append(frequency_monthly_min2)

                        quarterly_mean.append(frequency_quaterly_mean1)
                        quarterly_mean.append(frequency_quaterly_mean2)
                        quarterly_std_dev.append(frequency_quaterly_std_dev1)
                        quarterly_std_dev.append(frequency_quaterly_std_dev2)
                        quarterly_max.append(frequency_quaterly_max1)
                        quarterly_max.append(frequency_quaterly_max2)
                        quarterly_min.append(frequency_quaterly_min1)
                        quarterly_min.append(frequency_quaterly_min2)

                        yearly_mean.append(frequency_yearly_mean1)
                        yearly_mean.append(frequency_yearly_mean2)
                        yearly_std_dev.append(frequency_yearly_std_dev1)
                        yearly_std_dev.append(frequency_yearly_std_dev2)
                        yearly_max.append(frequency_yearly_max1)
                        yearly_max.append(frequency_yearly_max2)
                        yearly_min.append(frequency_yearly_min1)
                        yearly_min.append(frequency_yearly_min2)

                        if choice[i] == 'Monthly' or choice[i] == 'monthly':

                            data_send.append(monthly_mean[-1])
                            data_send.append(monthly_mean[-2])
                            data_send.append(monthly_std_dev[-1])
                            data_send.append(monthly_std_dev[-2])
                            data_send.append(monthly_max[-1])
                            data_send.append(monthly_max[-2])
                            data_send.append(monthly_min[-1])
                            data_send.append(monthly_min[-2])
                            sums.append(sum_monthly_1)
                            sums.append(sum_monthly_2)

                        elif choice[i] == 'Quarterly' or choice[i] == 'quarterly':
                            data_send.append(quarterly_mean[-1])
                            data_send.append(quarterly_mean[-2])
                            data_send.append(quarterly_std_dev[-1])
                            data_send.append(quarterly_std_dev[-2])
                            data_send.append(quarterly_max[-1])
                            data_send.append(quarterly_max[-2])
                            data_send.append(quarterly_min[-1])
                            data_send.append(quarterly_min[-2])
                            sums.append(sum_quaterly_1)
                            sums.append(sum_quaterly_2)

                        elif choice[i] == 'Yearly' or choice[i] == 'yearly':

                            data_send.append(yearly_mean[-1])
                            data_send.append(yearly_mean[-2])
                            data_send.append(yearly_std_dev[-1])
                            data_send.append(yearly_std_dev[-2])
                            data_send.append(yearly_max[-1])
                            data_send.append(yearly_max[-2])
                            data_send.append(yearly_min[-1])
                            data_send.append(yearly_min[-2])
                            sums.append(sum_yearly_1)
                            sums.append(sum_yearly_2)

                    elif frequencies[i] == 'Monthly' or frequencies[i] == 'monthly':
                        t = []

                        month = []

                        for k in range(len(dates)):
                        	c = dates[k]
                        	month.append(c[5:7])

                        for k in range(len(month)) :
                        	month[k] = int(month[k])


                        quaterly_data1 = []
                        quaterly_data2 = []

                        for k in range(len(month)-1):
                            if month[k] == 3 and month[k+1] != 3:
                                quaterly_data1.append(datas[k])

                            elif month[k] == 6 and month[k+1] != 6:
                                quaterly_data1.append(datas[k])

                            elif month[k] == 9 and month[k+1] != 9:
                                quaterly_data1.append(datas[k])

                            elif month[k] == 12 and month[k+1] != 12:
                                quaterly_data1.append(datas[k])

                        if month[-1] == 3 or month[-1] == 6 or month[-1] == 9 or month[-1] == 12:
                            quaterly_data1.append(datas[-1])

                        p = 0
                        for k in range(len(month)-1):
                            if month[k] == 3 and month[k+1] != 3:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                            elif month[k] == 6 and month[k+1] != 6:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                            elif month[k] == 9 and month[k+1] != 9:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                            elif month[k] == 12 and month[k+1] != 12:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))

                        if month[-1] == 3 or month[-1] == 6 or month[-1] == 9 or month[-1] == 12:
                            if month[-1] != month[-2]:
                                quaterly_data2.append(datas[-1])
                            else:
                                t = datas[p:k]
                                p = k+1
                                quaterly_data2.append(statistics.mean(t))


                        t.clear()


                        yearly_data1 = []
                        yearly_data2 = []
                        year = []

                        for k in range(len(dates)):
                        	year.append(dates[k][0:4])

                        for k in range(len(year)-1):
                        	if year[k] != year[k+1]:
                        		yearly_data1.append(datas[k])

                        yearly_data1.append(datas[len(datas)-1])

                        flag = 0
                        for k in range(len(year)-1):
                            if year[k] == year[k+1]:
                                flag = 1
                                t.append(datas[k])

                            elif year[k] != year[k+1]:
                                flag = -1
                                t.append(datas[k])
                                yearly_data2.append(statistics.mean(t))
                                t.clear()

                        if flag == 1:
                            t.append(datas[-1])
                            yearly_data2.append(statistics.mean(t))
                            t.clear()

                        else:
                            yearly_data2.append(datas[-1])
                            t.clear()

                        t.clear()


                        frequency_quaterly_mean1 = statistics.mean(quaterly_data1)
                        frequency_quaterly_mean2 = statistics.mean(quaterly_data2)
                        frequency_quaterly_std_dev1 = statistics.stdev(quaterly_data1)
                        frequency_quaterly_std_dev2 = statistics.stdev(quaterly_data2)
                        frequency_quaterly_max1 = max(quaterly_data1)
                        frequency_quaterly_max2 = max(quaterly_data2)
                        frequency_quaterly_min1 = max(quaterly_data1)
                        frequency_quaterly_min2 = min(quaterly_data2)
                        sum_quaterly_1 = sum(quaterly_data1)
                        sum_quaterly_2 = sum(quaterly_data2)

                        frequency_yearly_mean1 = statistics.mean(yearly_data1)
                        frequency_yearly_mean2 = statistics.mean(yearly_data2)
                        frequency_yearly_std_dev1 = statistics.stdev(yearly_data1)
                        frequency_yearly_std_dev2 = statistics.stdev(yearly_data2)
                        frequency_yearly_max1 = max(yearly_data1)
                        frequency_yearly_max2 = max(yearly_data2)
                        frequency_yearly_min1 = max(yearly_data1)
                        frequency_yearly_min2 = min(yearly_data2)
                        sum_yearly_1 = sum(yearly_data1)
                        sum_yearly_2 = sum(yearly_data2)

                        quarterly_mean.append(frequency_quaterly_mean1)
                        quarterly_mean.append(frequency_quaterly_mean2)
                        quarterly_std_dev.append(frequency_quaterly_std_dev1)
                        quarterly_std_dev.append(frequency_quaterly_std_dev2)
                        quarterly_max.append(frequency_quaterly_max1)
                        quarterly_max.append(frequency_quaterly_max2)
                        quarterly_min.append(frequency_quaterly_min1)
                        quarterly_min.append(frequency_quaterly_min2)


                        yearly_mean.append(frequency_yearly_mean1)
                        yearly_mean.append(frequency_yearly_mean2)
                        yearly_std_dev.append(frequency_yearly_std_dev1)
                        yearly_std_dev.append(frequency_yearly_std_dev2)
                        yearly_max.append(frequency_yearly_max1)
                        yearly_max.append(frequency_yearly_max2)
                        yearly_min.append(frequency_yearly_min1)
                        yearly_min.append(frequency_yearly_min2)



                        if choice[i] == 'Quarterly' or choice[i] == 'quarterly':
                            data_send.append(quarterly_mean[-1])
                            data_send.append(quarterly_mean[-2])
                            data_send.append(quarterly_std_dev[-1])
                            data_send.append(quarterly_std_dev[-2])
                            data_send.append(quarterly_max[-1])
                            data_send.append(quarterly_max[-2])
                            data_send.append(quarterly_min[-1])
                            data_send.append(quarterly_min[-2])
                            sums.append(sum_quaterly_1)
                            sums.append(sum_quaterly_2)

                        if choice[i] == 'Yearly' or choice[i] == 'yearly':

                            data_send.append(yearly_mean[-1])
                            data_send.append(yearly_mean[-2])
                            data_send.append(yearly_std_dev[-1])
                            data_send.append(yearly_std_dev[-2])
                            data_send.append(yearly_max[-1])
                            data_send.append(yearly_max[-2])
                            data_send.append(yearly_min[-1])
                            data_send.append(yearly_min[-2])
                            sums.append(sum_yearly_1)
                            sums.append(sum_yearly_2)

                elif frequencies[i] == 'Quarterly' or frequencies[i] == 'quarterly':

                    yearly_data1 = []
                    yearly_data2 = []
                    year = []

                    for k in range(len(dates)):
                    	year.append(dates[k][0:4])

                    for k in range(len(year)-1):
                    	if year[k] != year[k+1]:
                    		yearly_data1.append(datas[k])

                    yearly_data1.append(datas[len(datas)-1])

                    flag = 0
                    for k in range(len(year)-1):
                        if year[k] == year[k+1]:
                            flag = 1
                            t.append(datas[k])

                        elif year[k] != year[k+1]:
                            flag = -1
                            t.append(datas[k])
                            yearly_data2.append(statistics.mean(t))
                            t.clear()

                    if flag == 1:
                        t.append(datas[-1])
                        yearly_data2.append(statistics.mean(t))
                        t.clear()

                    else:
                        yearly_data2.append(datas[-1])
                        t.clear()

                    t.clear()


                    frequency_yearly_mean1 = statistics.mean(yearly_data1)
                    frequency_yearly_mean2 = statistics.mean(yearly_data2)
                    frequency_yearly_std_dev1 = statistics.stdev(yearly_data1)
                    frequency_yearly_std_dev2 = statistics.stdev(yearly_data2)
                    frequency_yearly_max1 = max(yearly_data1)
                    frequency_yearly_max2 = max(yearly_data2)
                    frequency_yearly_min1 = max(yearly_data1)
                    frequency_yearly_min2 = min(yearly_data2)
                    sum_yearly_1 = sum(yearly_data1)
                    sum_yearly_2 = sum(yearly_data2)

                    yearly_mean.append(frequency_yearly_mean1)
                    yearly_mean.append(frequency_yearly_mean2)
                    yearly_std_dev.append(frequency_yearly_std_dev1)
                    yearly_std_dev.append(frequency_yearly_std_dev2)
                    yearly_max.append(frequency_yearly_max1)
                    yearly_max.append(frequency_yearly_max2)
                    yearly_min.append(frequency_yearly_min1)
                    yearly_min.append(frequency_yearly_min2)

                    if choice[i] == 'Yearly' or choice[i] == 'yearly':

                        data_send.append(yearly_mean[-1])
                        data_send.append(yearly_mean[-2])
                        data_send.append(yearly_std_dev[-1])
                        data_send.append(yearly_std_dev[-2])
                        data_send.append(yearly_max[-1])
                        data_send.append(yearly_max[-2])
                        data_send.append(yearly_min[-1])
                        data_send.append(yearly_min[-2])
                        sums.append(sum_yearly_1)
                        sums.append(sum_yearly_2)

        if len(ids) > 1:
            corr_id_1 = int(request.form.get('id1'))
            corr_id_2 = int(request.form.get('id2'))

            object2_corr = Index.query.filter_by(id=corr_id_2).first()
            object1_corr = Index.query.filter_by(id=corr_id_1).first()

            rel_object1_corr = object1_corr.ref_data.all()
            rel_object2_corr = object2_corr.ref_data.all()

            data_corr1 = []
            data_corr2 = []

            for i in range(len(rel_object1_corr)):
                data_corr1.append(rel_object1_corr[i].data)

            for i in range(len(rel_object2_corr)):
                data_corr2.append(rel_object2_corr[i].data)

            if len(data_corr1) == len(data_corr2):
                pearson_corr, i = pearsonr(data_corr1, data_corr2)

            else:
                if len(data_corr1) < len(data_corr2):
                    data_corr2 = data_corr2[:len(data_corr1)]

                if len(data_corr2) < len(data_corr1):
                    data_corr1 = data_corr1[:len(data_corr2)]

                pearson_corr, i = pearsonr(data_corr1, data_corr2)

        mov_avg_id = int(request.form.get('mov_avg1'))
        mov_avg_period = int(request.form.get('mov_avg2'))

        object_mov_avg = Index.query.filter_by(id=mov_avg_id).first()

        rel_object_mov_avg = object_mov_avg.ref_data.all()

        mov_avg_data = []
        mov_avg = []

        for i in range(len(rel_object_mov_avg)):
            mov_avg_data.append(rel_object_mov_avg[i].data)

        if len(mov_avg_data) < mov_avg_period:
            mov_avg.append("Error Input")

        else:
            i = 0
            j = mov_avg_period-1

            while(j < len(mov_avg_data)):
                temp = mov_avg_data[i:j+1]
                mov_avg.append(statistics.mean(temp))
                i += 1
                j += 1

        if len(ids) > 1:
            return render_template('basic.html',sum=sums,pearson_corr=pearson_corr,mov_avg=mov_avg,choice=choice,lc=len(choice),q=q,data=data_send,ld=len(data_send),id=ids,len_id=len(ids))
        else:
            return render_template('basic.html',sum=sums,mov_avg=mov_avg,choice=choice,lc=len(choice),q=q,data=data_send,ld=len(data_send),id=ids,len_id=len(ids))


    else:
        q = 0
        return render_template('index.html',id=ids,frequency=frequencies,q=q,len_id=len(ids))


@app.route('/period/add',methods = ['GET','POST'])
def period():
    a = request.args.get("id")
    x = []
    ids = []
    q = 1
    c = a.find(',')

    if c == -1:
        ids.append(int(a[1:len(a)-1]))

    else:
        for i in range(len(a)):
            if a[i] == ',':
                x.append(i)
        b = 1
        for i in range(len(x)):
            ids.append(int(a[b:x[i]]))
            b = x[i]+1
        i = len(a)-1
        ids.append(int(a[x[-1]+1:i]))

    object = []

    for i in range(len(ids)):
        f = Index.query.filter_by(id=ids[i]).first()
        object.append(f)

    if request.method == 'POST':
        datas = []
        dates = []
        mean = []
        std_dev = []
        maxs = []
        mins = []
        sums = []

        for i in range(len(object)):
            dates.clear()
            datas.clear()

            l = object[i].ref_data.all()

            if len(l) != 0:
                for k in range(len(l)):
                    datas.append(l[k].data)
                    dates.append(l[k].date)

            min_date = request.form.get(dates[0])
            max_date = request.form.get(dates[-1])

            min_ind = -1
            max_ind = -1

            for i in range(len(dates)):
                if dates[i] >= min_date:
                    min_ind = i
                    break

            for i in range(len(dates)-1,0,-1):
                if dates[i] <= max_date:
                    max_ind = i
                    break

            date = dates[min_ind:max_ind+1]
            data = datas[min_ind:max_ind+1]

            sums.append(sum(data))

            mean.append(statistics.mean(data))
            std_dev.append(statistics.mean(data))
            maxs.append(max(data))
            mins.append(min(data))

        if len(ids) > 1:
            corr_id_1 = int(request.form.get('id1'))
            corr_id_2 = int(request.form.get('id2'))

            object2_corr = Index.query.filter_by(id=corr_id_2).first()
            object1_corr = Index.query.filter_by(id=corr_id_1).first()

            rel_object1_corr = object1_corr.ref_data.all()
            rel_object2_corr = object2_corr.ref_data.all()

            data_corr1 = []
            data_corr2 = []

            for i in range(len(rel_object1_corr)):
                data_corr1.append(rel_object1_corr[i].data)

            for i in range(len(rel_object2_corr)):
                data_corr2.append(rel_object2_corr[i].data)

            if len(data_corr1) == len(data_corr2):
                pearson_corr, i = pearsonr(data_corr1, data_corr2)

            else:
                if len(data_corr1) < len(data_corr2):
                    data_corr2 = data_corr2[:len(data_corr1)]

                if len(data_corr2) < len(data_corr1):
                    data_corr1 = data_corr1[:len(data_corr2)]

                pearson_corr, i = pearsonr(data_corr1, data_corr2)

        mov_avg_id = int(request.form.get('mov_avg1'))
        mov_avg_period = int(request.form.get('mov_avg2'))

        object_mov_avg = Index.query.filter_by(id=mov_avg_id).first()

        rel_object_mov_avg = object_mov_avg.ref_data.all()

        mov_avg_data = []
        mov_avg = []

        for i in range(len(rel_object_mov_avg)):
            mov_avg_data.append(rel_object_mov_avg[i].data)

        if len(mov_avg_data) < mov_avg_period:
            mov_avg.append("Error Input")

        else:
            i = 0
            j = mov_avg_period-1

            while(j < len(mov_avg_data)):
                temp = mov_avg_data[i:j+1]
                mov_avg.append(statistics.mean(temp))
                i += 1
                j += 1

        if len(ids) > 1:
            return render_template('period1.html',sum=sums,id=ids,mean=mean,std_dev=std_dev,max=maxs,min=mins,len=len(mean),mov_avg=mov_avg,pearson_corr=pearson_corr)
        else:
            return render_template('period1.html',id=ids,mean=mean,std_dev=std_dev,max=maxs,min=mins,len=len(mean),mov_avg=mov_avg)

    else:
        dates = []
        date_send = []

        for i in range(len(object)):

            l = object[i].ref_data.all()

            if len(l) != 0:
                for k in range(len(l)):
                    dates.append(l[k].date)

                date_send.append(dates[0])
                date_send.append(dates[-1])

                dates.clear()

        return render_template('period.html',id=ids,date=date_send,len=len(ids))

if  __name__ == 'main':
    app.run(debug=True)

