from flask import Flask,request, render_template, flash, redirect, url_for,session, logging, send_file
from flask_mysqldb import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateTimeField, BooleanField, IntegerField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from functools import wraps
from werkzeug.utils import secure_filename
from coolname import generate_slug
from datetime import timedelta, datetime
from flask import render_template_string
import functools
import math, random 
import json
import csv
import smtplib
from wtforms_components import TimeField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'mysql.stackcp.com'
app.config['MYSQL_USER'] = 'quizapp-313537b23f'
app.config['MYSQL_PORT'] = 54375
app.config['MYSQL_PASSWORD'] = 'narenderBoi1'
app.config['MYSQL_DB'] = 'quizapp-313537b23f'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.secret_key= 'ca2'

sender = 'care@narenderkeswani.com'

mysql = MySQL(app)

@app.before_request
def make_session_permanent():
	session.permanent = True
	app.permanent_session_lifetime = timedelta(minutes=10)

def is_logged(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login','danger')
			return redirect(url_for('login'))
	return wrap

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
	if request.method == 'POST':
		careEmail = "narender.rk10@gmail.com"
		cname = request.form['cname']
		cemail = request.form['cemail']
		cquery = request.form['cquery']
		msgtocc = " ".join(["NAME:", cname, "EMAIL:", cemail, "QUERY:", cquery]) 
		server1 = smtplib.SMTP('smtp.stackmail.com',587)
		server1.ehlo()
		server1.starttls()
		server1.ehlo()
		server1.login('care@narenderkeswani.com', 'Narender@boi')
		server1.sendmail(sender,cemail,"YOUR QUERY WILL BE PROCESSED!")
		msgtocc = " ".join(["NME:", cname, "EMAIL:", cemail, "QUERY:", cquery]) 
		server1.sendmail(sender, careEmail, msgtocc)
		server1.quit()
		flash('Your Query has been recorded.', 'success')
	return render_template('contact.html')

@app.route('/lostpassword', methods=['GET','POST'])
def lostpassword():
	if request.method == 'POST':
		lpemail = request.form['lpemail']
		cur = mysql.connection.cursor()
		results = cur.execute('SELECT * from users where email = %s' , [lpemail])
		if results > 0:
			server = smtplib.SMTP('smtp.stackmail.com',587)
			server.ehlo()
			server.starttls()
			server.ehlo()
			server.login('care@narenderkeswani.com', 'Narender@boi')
			sesOTPfp = generateOTP()
			session['tempOTPfp'] = sesOTPfp
			session['seslpemail'] = lpemail
			server.sendmail(sender, lpemail, "Your OTP Verfication code for reset password is "+sesOTPfp+".")
			server.quit()
			return redirect(url_for('verifyOTPfp')) 
		else:
			return render_template('lostpassword.html',error="Account not found.")
	return render_template('lostpassword.html')

@app.route('/verifyOTPfp', methods=['GET','POST'])
def verifyOTPfp():
	if request.method == 'POST':
		fpOTP = request.form['fpotp']
		fpsOTP = session['tempOTPfp']
		if(fpOTP == fpsOTP):
			return redirect(url_for('lpnewpwd')) 
	return render_template('verifyOTPfp.html')

@app.route('/lpnewpwd', methods=['GET','POST'])
def lpnewpwd():
	if request.method == 'POST':
		npwd = request.form['npwd']
		cpwd = request.form['cpwd']
		slpemail = session['seslpemail']
		if(npwd == cpwd ):
			cur = mysql.connection.cursor()
			cur.execute('UPDATE users set password = %s where email = %s', (npwd, slpemail))
			mysql.connection.commit()
			cur.close()
			session.clear()
			return render_template('login.html',success="Your password was sucessfully changed.")
		else:
			return render_template('login.html',error="Password doesn't matched.")
	return render_template('lpnewpwd.html')

@app.route('/changepassword')
@is_logged
def changepassword():
	return render_template('changepassword.html')

def generateOTP() : 
    digits = "0123456789"
    OTP = "" 
    for i in range(5) : 
        OTP += digits[math.floor(random.random() * 10)] 
    return OTP 

@app.route('/register', methods=['GET','POST'])
def register():
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		username = request.form['username']
		password = request.form['password']
		cpassword = request.form['cpassword']
		if(password == cpassword):
			session['tempName'] = name
			session['tempName'] = name
			session['tempEmail'] = email
			session['tempUsername'] = username
			session['tempPassword'] = password
			server = smtplib.SMTP('smtp.stackmail.com',587)
			server.ehlo()
			server.starttls()
			server.ehlo()
			server.login('care@narenderkeswani.com', 'Narender@boi')
			sesOTP = generateOTP()
			session['tempOTP'] = sesOTP
			server.sendmail(sender, email, "Your OTP Verfication code is "+sesOTP+".")
			server.quit()
			return redirect(url_for('verifyEmail')) 
	return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']
		cur = mysql.connection.cursor()
		results = cur.execute('SELECT * from users where username = %s' , [username])
		if results > 0:
			data = cur.fetchone()
			password = data['password']
			confirmed = data['confirmed']
			name = data['name']
			if confirmed == 0:
				error = 'Please confirm email before logging in'
				return render_template('login.html', error=error)
			if confirmed == 1 and password == password_candidate:
				session['logged_in'] = True
				session['username'] = username
				session['name'] = name
				return redirect(url_for('dashboard'))
			else:
				error = 'Invalid password'
				return render_template('login.html', error=error)
			cur.close()
		else:
			error = 'Username not found'
			return render_template('login.html', error=error)
	return render_template('login.html')

@app.route('/verifyEmail', methods=['GET','POST'])
def verifyEmail():
	if request.method == 'POST':
		theOTP = request.form['eotp']
		mOTP = session['tempOTP']
		dbName = session['tempName']
		dbEmail = session['tempEmail']
		dbUsername = session['tempUsername']
		dbPassword = session['tempPassword']
		if(theOTP == mOTP):
			cur = mysql.connection.cursor()
			cur.execute('INSERT INTO users(username,name,email, password,confirmed) values(%s,%s,%s,%s,1)', (dbUsername, dbName, dbEmail, dbPassword))
			mysql.connection.commit()
			cur.close()
			session.clear()
			return render_template('login.html',success="Thanks for registering! You are sucessfully verified.")
		else:
			return render_template('register.html',error="OTP is incorrect.")
	return render_template('verifyEmail.html')

@app.route('/changepassword', methods=["GET", "POST"])
def changePassword():
	if request.method == "POST":
		oldPassword = request.form['oldpassword']
		newPassword = request.form['newpassword']
		cur = mysql.connection.cursor()
		results = cur.execute("SELECT * from users where username = '" + session['username'] + "'")
		if results > 0:
			data = cur.fetchone()
			password = data['password']
			if(password == oldPassword):
				cur.execute("UPDATE users SET password = %s WHERE username = %s", [newPassword,session['username']])
				mysql.connection.commit()
				msg="Changed successfully"
				flash('Changed successfully.', 'success')
				cur.close()
				return render_template("changepassword.html", success=msg)
			else:
				error = "Wrong password"
				return render_template("changepassword.html", error=error)
		else:
			return render_template("changepassword.html")

@app.route('/dashboard')
@is_logged
def dashboard():
	return render_template('dashboard.html')

@app.route('/logout')
def logout():
	session.clear()
	flash('Successfully logged out', 'success')
	return redirect(url_for('index'))

class UploadForm(FlaskForm):
	subject = StringField('Subject')
	topic = StringField('Topic')
	doc = FileField('CSV Upload', validators=[FileRequired()])
	start_date = DateField('Start Date')
	start_time = TimeField('Start Time', default=datetime.utcnow()+timedelta(hours=5.5))
	end_date = DateField('End Date')
	end_time = TimeField('End Time', default=datetime.utcnow()+timedelta(hours=5.5))
	password = StringField('Test Password', [validators.Length(min=3, max=6)])

	def validate_end_date(form, field):
		if field.data < form.start_date.data:
			raise ValidationError("End date must not be earlier than start date.")
	
	def validate_end_time(form, field):
		start_date_time = datetime.strptime(str(form.start_date.data) + " " + str(form.start_time.data),"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
		end_date_time = datetime.strptime(str(form.end_date.data) + " " + str(field.data),"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
		if start_date_time >= end_date_time:
			raise ValidationError("End date time must not be earlier/equal than start date time")
	
	def validate_start_date(form, field):
		if datetime.strptime(str(form.start_date.data) + " " + str(form.start_time.data),"%Y-%m-%d %H:%M:%S") < datetime.now():
			raise ValidationError("Start date and time must not be earlier than current")

class TestForm(Form):
	test_id = StringField('Test ID')
	password = PasswordField('Test Password')

@app.route('/create-test', methods = ['GET', 'POST'])
@is_logged
def create_test():
	form = UploadForm()
	if request.method == 'POST' and form.validate_on_submit():
		f = form.doc.data
		filename = secure_filename(f.filename)
		f.save('questions/' + filename)
		test_id = generate_slug(2)
		with open('questions/' + filename) as csvfile:
			reader = csv.DictReader(csvfile, delimiter = ',')
			cur = mysql.connection.cursor()
			for row in reader:
				cur.execute('INSERT INTO questions(test_id,qid,q,a,b,c,d,ans,marks) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (test_id, row['qid'], row['q'], row['a'], row['b'], row['c'], row['d'], row['ans'], 1 ))
			cur.connection.commit()
			start_date = form.start_date.data
			end_date = form.end_date.data
			start_time = form.start_time.data
			end_time = form.end_time.data
			start_date_time = str(start_date) + " " + str(start_time)
			end_date_time = str(end_date) + " " + str(end_time)
			password = form.password.data
			subject = form.subject.data
			topic = form.topic.data
			cur.execute('INSERT INTO teachers (username, test_id, start, end, password, subject, topic) values(%s,%s,%s,%s,%s,%s,%s)',
			(dict(session)['username'], test_id, start_date_time, end_date_time, password, subject, topic))
			cur.connection.commit()
			cur.close()
			flash(f'Test ID: {test_id}', 'success')
			return redirect(url_for('dashboard'))
	return render_template('create_test.html' , form = form)

@app.route('/deltidlist', methods=['GET'])
@is_logged
def deltidlist():
	cur = mysql.connection.cursor()
	results = cur.execute('SELECT test_id from teachers where username = %s', [session['username']])
	if results > 0:
		cresults = cur.fetchall()
		cur.close()
		return render_template("deltidlist.html", cresults = cresults)

@app.route('/deldispques', methods=['GET','POST'])
@is_logged
def deldispques():
	if request.method == 'POST':
		tidoption = request.form['choosetid']
		cur = mysql.connection.cursor()
		cur.execute('SELECT * from questions where test_id = %s', [tidoption])
		callresults = cur.fetchall()
		cur.close()
		return render_template("deldispques.html", callresults = callresults)

@app.route('/<testid>/<qid>')
@is_logged
def del_qid(testid, qid):
	cur = mysql.connection.cursor()
	results = cur.execute('DELETE FROM questions where test_id = %s and qid =%s', (testid,qid))
	mysql.connection.commit()
	if results>0:
		msg="Deleted successfully"
		flash('Deleted successfully.', 'success')
		cur.close()
		return render_template("deldispques.html", success=msg)
	else:
		return redirect(url_for('dashboard'))

@app.route('/updatetidlist', methods=['GET'])
@is_logged
def updatetidlist():
	cur = mysql.connection.cursor()
	results = cur.execute('SELECT test_id from teachers where username = %s', [session['username']])
	if results > 0:
		cresults = cur.fetchall()
		cur.close()
		return render_template("updatetidlist.html", cresults = cresults)

@app.route('/updatedispques', methods=['GET','POST'])
@is_logged
def updatedispques():
	if request.method == 'POST':
		tidoption = request.form['choosetid']
		cur = mysql.connection.cursor()
		cur.execute('SELECT * from questions where test_id = %s', [tidoption])
		callresults = cur.fetchall()
		cur.close()
		return render_template("updatedispques.html", callresults = callresults)

@app.route('/update/<testid>/<qid>', methods=['GET','POST'])
@is_logged
def update_quiz(testid, qid):
	if request.method == 'GET':
		cur = mysql.connection.cursor()
		cur.execute('SELECT * FROM questions where test_id = %s and qid =%s', (testid,qid))
		uresults = cur.fetchall()
		mysql.connection.commit()
		return render_template("updateQuestions.html", uresults=uresults)
	if request.method == 'POST':
		ques = request.form['ques']
		ao = request.form['ao']
		bo = request.form['bo']
		co = request.form['co']
		do = request.form['do']
		anso = request.form['anso']
		cur = mysql.connection.cursor()
		cur.execute('UPDATE questions SET q = %s, a = %s, b = %s, c = %s, d = %s, ans = %s where test_id = %s and qid = %s', (ques,ao,bo,co,do,anso,testid,qid))
		cur.connection.commit()
		msg="Updated successfully"
		flash('Updated successfully.', 'success')
		cur.close()
		return render_template("updatedispques.html", success=msg)
	else:
		msg="ERROR  OCCURED."
		flash('ERROR  OCCURED.', 'error')
		return redirect(url_for('updatedispques', error=msg))

@app.route('/viewquestions', methods=['GET'])
@is_logged
def viewquestions():
	cur = mysql.connection.cursor()
	results = cur.execute('SELECT test_id from teachers where username = %s', [session['username']])
	if results > 0:
		cresults = cur.fetchall()
		cur.close()
		return render_template("viewquestions.html", cresults = cresults)

@app.route('/displayquestions', methods=['GET','POST'])
@is_logged
def displayquestions():
	if request.method == 'POST':
		tidoption = request.form['choosetid']
		cur = mysql.connection.cursor()
		cur.execute('SELECT * from questions where test_id = %s', [tidoption])
		callresults = cur.fetchall()
		cur.close()
		return render_template("displayquestions.html", callresults = callresults)

@app.route('/give-test/<testid>', methods=['GET','POST'])
@is_logged
def test(testid):
	if request.method == 'GET':
		cur = mysql.connection.cursor()
		results = cur.execute('SELECT * from questions where test_id = %s',[testid])
		results = cur.fetchall()
		cur.close()
		cur = mysql.connection.cursor()
		results2 = cur.execute('SELECT end from teachers where test_id = %s',[testid])
		results2 = cur.fetchall()
		cur.close()
		return render_template("testquiz.html", callresults = results, callresults2 = results2)
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		results1 = cur.execute('SELECT COUNT(qid) from questions where test_id = %s',[testid])
		results1 = cur.fetchone()
		cur.close()
		completed=1
		for sa in range(1,results1['COUNT(qid)']+1):
			answerByStudent = request.form[str(sa)]
			cur = mysql.connection.cursor()
			cur.execute('INSERT INTO students values(%s,%s,%s,%s)', (session['username'], testid, sa, answerByStudent))
			mysql.connection.commit()
		cur.execute('INSERT INTO studentTestInfo values(%s,%s,%s)', (session['username'], testid, completed))
		mysql.connection.commit()
		cur.close()
		flash('Successfully Test Submitted', 'success')
		return redirect(url_for('dashboard'))

@app.route("/give-test", methods = ['GET', 'POST'])
@is_logged
def give_test():
	global duration, marked_ans	
	form = TestForm(request.form)
	if request.method == 'POST' and form.validate():
		test_id = form.test_id.data
		password_candidate = form.password.data
		cur = mysql.connection.cursor()
		results = cur.execute('SELECT * from teachers where test_id = %s', [test_id])
		if results > 0:
			data = cur.fetchone()
			password = data['password']
			start = data['start']
			start = str(start)
			end = data['end']
			end = str(end)
			if password == password_candidate:
				now = datetime.now()
				now = now.strftime("%Y-%m-%d %H:%M:%S")
				now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
				if datetime.strptime(start,"%Y-%m-%d %H:%M:%S") < now and datetime.strptime(end,"%Y-%m-%d %H:%M:%S") > now:
					results = cur.execute('SELECT completed from studentTestInfo where username = %s and test_id = %s', (session['username'], test_id))
					if results > 0:
						results = cur.fetchone()
						is_completed = results['completed']
						if is_completed == 0:
							return redirect(url_for('test' , testid = test_id))
						else:
							flash('Test already given', 'success')
							return redirect(url_for('give_test'))
				else:
					if datetime.strptime(start,"%Y-%m-%d %H:%M:%S") > now:
						flash(f'Test start time is {start}', 'danger')
					else:
						flash(f'Test has ended', 'danger')
					return redirect(url_for('give_test'))
				return redirect(url_for('test' , testid = test_id))
			else:
				flash('Invalid password', 'danger')
				return redirect(url_for('give_test'))
		flash('Invalid testid', 'danger')
		return redirect(url_for('give_test'))
		cur.close()
	return render_template('give_test.html', form = form)

def totmarks(username,tests): 
	cur = mysql.connection.cursor()
	for test in tests:
		testid = test['test_id']
		results = cur.execute("select sum(marks) as totalmks from students s,questions q \
			where s.username=%s and s.test_id=%s and s.qid=q.qid and s.test_id=q.test_id \
			and s.ans=q.ans", (username, testid))				
		results = cur.fetchone()
		if str(results['totalmks']) == 'None':
			results['totalmks'] = 0
		test['marks'] = results['totalmks']
		if "Decimal" not in str(results['totalmks']): 
			mstr = str(results['totalmks']).replace('Decimal', '')
			results['totalmks'] = mstr
			test['marks'] = results['totalmks']
	return tests

def marks_calc(username,testid):
	if username == session['username']:
		cur = mysql.connection.cursor()
		results = cur.execute("select sum(marks) as totalmks from students s,questions q \
			where s.username=%s and s.test_id=%s and s.qid=q.qid and s.test_id=q.test_id \
			and s.ans=q.ans", (username, testid))
		results = cur.fetchone()
		if str(results['totalmks']) == 'None':
			results['totalmks'] = 0
			return results['totalmks']
		if "Decimal" not in str(results['totalmks']): 
			mstr = str(results['totalmks']).replace('Decimal', '')
			results['totalmks'] = mstr
			return results['totalmks']
		else:
			return results['totalmks']
		
@app.route('/<username>/tests-given')
@is_logged
def tests_given(username):
	if username == session['username']:
		cur = mysql.connection.cursor()
		results = cur.execute('select distinct(students.test_id),subject,topic from students,teachers where students.username = %s and students.test_id=teachers.test_id', [username])
		results = cur.fetchall()
		results = totmarks(username,results)
		return render_template('tests_given.html', tests=results)
	else:
		flash('You are not authorized', 'danger')
		return redirect(url_for('dashboard'))

@app.route('/<username>/tests-created/<testid>', methods = ['POST','GET'])
@is_logged
def student_results(username, testid):
	if username == session['username']:
		cur = mysql.connection.cursor()
		results = cur.execute('select users.name as name,users.username as username,test_id from studentTestInfo,users where test_id = %s and completed = 1 and studentTestInfo.username=users.username ', [testid])
		results = cur.fetchall()
		final = []
		count = 1
		for user in results:
			score = marks_calc(user['username'], testid)
			user['srno'] = count
			user['marks'] = score
			final.append([count, user['name'], score])
			count+=1
		if request.method =='GET':
			return render_template('student_results.html', data=final)
		else:
			fields = ['Sr No', 'Name', 'Marks']
			with open('static/' + testid + '.csv', 'w') as f:
				writer = csv.writer(f)
				writer.writerow(fields)
				writer.writerows(final)
			return send_file('/static/' + testid + '.csv', as_attachment=True)

@app.route('/<username>/tests-created')
@is_logged
def tests_created(username):
	if username == session['username']:
		cur = mysql.connection.cursor()
		results = cur.execute('select * from teachers where username = %s', [username])
		results = cur.fetchall()
		return render_template('tests_created.html', tests=results)
	else:
		flash('You are not authorized', 'danger')
		return redirect(url_for('dashboard'))

if __name__ == "__main__":
	app.run(host = "0.0.0.0",debug=True)