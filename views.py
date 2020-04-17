from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import random
import re
import os

UPLOAD_FOLDER='static/media'
app=Flask(__name__)
app.secret_key = "abc"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
conn = sqlite3.connect('KM.db')
conn.execute("")
@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method=="GET" and 'emailId' not in session:
        return render_template("signup.html")
    elif(request.method=="POST") and 'emailId' not in session:
        try:
            data=request.form
            conn = sqlite3.connect('KM.db')
            c=conn.cursor()
            c.execute("insert into lecture(email,fname,lname,password,phone,gender) values('"+data['emailId']+"','"+data['name']+"','"+data['branch']+"','"+data['password']+"','"+data['phone']+"','"+data['gender']+"');")
            conn.commit()
            return redirect('/signin')
        except Exception as e:
        	print(e,data)
        	return render_template('signup.html',data="Username Already Exists")
    else:
    	return redirect('/')

@app.route('/studentPassword',methods=["GET","POST"])
def studentSet():
	if request.method=="GET":
		return render_template("student.html",msg="")
	else:
		data=request.form
		conn = sqlite3.connect('KM.db')
		c=conn.cursor()
		c.execute("select * from student where srn='"+data['srn']+"' and emailID='"+data['email']+"';")
		a=list(map(lambda x:list(x),list(c)))
		print(list(c),len(list(c)))
		print(a,len(a))
		if(a==0):
			return render_template("student.html",msg="Student Does not exist")
		else:
			print(list(c),len(list(c)))
			if(a[0][8]!=""):
				return render_template("student.html",msg="Password Alredy Set Can't alter")
			c.execute("update student set password='"+data['password']+"' where emailId='"+data['email']+"' and srn='"+data['srn']+"';")
			conn.commit()
			return redirect('/signin')


@app.route('/signin',methods=["GET","POST"])
def signin():
    if request.method=="GET" and 'emailId' not in session:
        return render_template("signin.html")
    elif 'emailId' not in session:
        data=request.form
        conn = sqlite3.connect('KM.db')
        c=conn.cursor()
        d=conn.cursor()
        c.execute("select * from student where emailId='"+data['emailId']+"' and password='"+data['password']+"';")
        d.execute("select * from lecture where email='"+data['emailId']+"' and password='"+data['password']+"';")
        c=list(c)
        d=list(d)
        print(c)
        if(len(c)>0):
        	e=c
        	session['lec']=0
        	session['admin']=0
        elif(len(d)>0):
        	e=d
        	session['lec']=1
        	if d[0][6]==1:
        		session['admin']=1
        	else:
        		session['admin']=0
        else:
        	return render_template('signin.html',data="Username and password does not match")    
        session['emailId']=data['emailId']
        msg="SignIn Successfull"
        return redirect('/')
    else:
    	return redirect('/')

@app.route('/signout')
def signout():
	if 'emailId' in session:
		del session['emailId']
		del session['lec']
		del session['admin']
		return redirect('/')
	else:
		abort(400)

@app.route('/brainstorm', methods=['GET','POST','DELETE'])
def brainstorm():
	conn = sqlite3.connect('KM.db')
	if 'emailId' in session:
		if request.method=="GET":
			if 'emailId' in session:
				c=conn.cursor()
				c.execute("select * from brainstorm;")
				c=list(c)
				return render_template('brainstorm.html',data=c)
			return redirect('/signin')
		elif request.method=="POST":
			data=request.form
			c=conn.cursor()
			date=str(datetime.now())
			c.execute("insert into brainstorm values('"+session['emailId']+"','"+date+"','"+data['post']+"');")
			conn.commit()
			return redirect('/brainstorm')
	else:
		return redirect('/signin')

@app.route('/brainRefresh')
def refresh():
	l=[]
	conn = sqlite3.connect('KM.db')
	e=conn.cursor()
	e.execute("select * from brainstorm;")
	e=list(e)
	for i in e:
		c=conn.cursor()
		d=conn.cursor()
		c.execute("select * from student where emailId='"+i[0]+"';")
		d.execute("select * from lecture where email='"+i[0]+"';")
		c=list(c)
		d=list(d)
		if(len(c)>0):
			l.append(0)
		elif(len(d)>0):
			if(d[0][6]==0):
				l.append(1)
			else:
				l.append(2)

	#print(render_template('chatbox.html',data=c))
	return render_template('chatbox.html',data=zip(e,l))
@app.route('/blog')
def blog():
	conn = sqlite3.connect('KM.db')
	hashtag=request.args.get('hashtag')
	if hashtag:
		c=conn.cursor()
		c.execute("select post_id from hashtag where hashtag='"+hashtag+"';")
		d=list(c)
		l=[]
		for i in d:
			c.execute("select * from blog where post_id="+str(i[0])+";")
			l.append(list(c)[0])
			print(c)
		print(l)
		return render_template('blog1.html',data=l)
	else:
		c=conn.cursor()
		c.execute("select * from blog;")
		c=list(c)
		return render_template('blog1.html',data=c)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
	conn = sqlite3.connect('KM.db')
	if request.method=="GET":
		if 'emailId' in session:
				return render_template('newpost.html')
		else:
			return redirect('/signin')
	elif request.method=="POST":
		try:
			data=request.form
			file = request.files['img']
			date=str(datetime.now())
			c=conn.cursor()
			filename = file.filename
			c.execute("insert into blog(posted_by,heading,datetime,post,img) values('"+session['emailId']+"','"+data['heading']+"','"+date+"','"+data['post']+"','"+filename+"');")
			conn.commit()
			c.execute("select post_id from blog where posted_by='"+session['emailId']+"' and heading='"+data['heading']+"';")
			post_id=list(c)[0][0]
			hashtags1=re.findall(r"#(\w+)", data['post'])
			hashtags2=re.findall(r"#(\w+)", data['hashtags'])
			hashtag=hashtags1+hashtags2
			print(post_id,hashtag)
			print(data)
			
			if file.filename!='':
				filename = file.filename
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			for i in hashtag:
				try:
					print(type(post_id),type(i))
					c.execute("insert into hashtag(post_id,hashtag) values("+str(post_id)+",'"+i+"');")
				except Exception as e:
					print("hastag reused",e)
			conn.commit()
			return redirect('/blog')
		except Exception as e:
			print(e)
			return redirect('/newpost')

@app.route('/post/<post_id>')
def post(post_id):
	conn = sqlite3.connect('KM.db')
	c=conn.cursor()
	c.execute("select * from blog where post_id="+post_id+";")
	e=list(c)[0]
	d={}
	d["post"]=e
	c.execute("select hashtag from hashtag where post_id="+post_id+";")
	l=[]
	l=list(map(lambda x: x[0],c))
	d["hashtag"]=l
	print(l)
	return render_template('post.html',data=d)

@app.route('/student_select',methods=["POST","GET"])
def student_select():
	if 'emailId' not in session:
		return redirect('/signin')
	elif session['lec']==0:
		abort(403)
	if(request.method=="GET"):
		return render_template("student_select.html")
	else:
		data=request.form
		conn = sqlite3.connect('KM.db')
		ct=conn.cursor()
		print(data)
		c=""
		w=""
		c_count=0
		w_count=0
		if(data["name"]==""):
			if(c_count==0):
				c=c+"name"
				c_count+=1
			else:
				c=c+" , "+ "name"
		elif(data["name"]!="No"):
			if(w_count==0):
				w=w+" name like \'" + data["name"] + "%\'"
				w_count=w_count+1
			else:
				w=w+" AND " + " name like \'" + data["name"] + "%\'"
		if(data["gender"]=="m"):
			if(w_count==0):
				w=w+" gender like \'" + "Male\'"
				w_count=w_count+1
			else:
				w=w+" AND "+" gender like \'" + "Male\'"
		elif(data["gender"]=="f"):
			if(w_count==0):
				w=w+" gender like \'" + "Female\'"
				w_count=w_count+1
			else:
				w=w+" AND "+" gender like \'" + "Female\'"
		elif(data["gender"]=="any"):
			if(c_count==0):
				c=c+"gender"
				c_count+=1
			else:
				c=c+" , "+"gender"
		if(data["srn"]==""):
			if(c_count==0):
				c=c+"srn"
				c_count+=1
			else:
				c=c+" , "+ "srn"
		elif(data["srn"]!="No"):
			if(w_count==0):
				w=w+" srn like \'" + data["srn"]+"\'"
				w_count=w_count+1
			else:
				w=w+" AND " + " srn like \'" + data["srn"]+"\'"
		if(data["emailid"]==""):
			if(c_count==0):
				c=c+"emailid"
				c_count+=1
			else:
				c=c+" , "+ "emailid"
		elif(data["emailid"]!="No"):
			if(w_count==0):
				w=w+" emailid like \'" + data["emailid"]+"\'"
				w_count=w_count+1
			else:
				w=w+" AND " + " emailid like " + data["emailid"]
		if(data["program"]==""):
			if(c_count==0):
				c=c+"program"
				c_count+=1
			else:
				c=c+" , "+ "program"
		elif(data["program"]!="No"):
			temp="B.Tech in "
			if(data["program"]=="CE"):
				temp=temp+"Civil Engineering"
			elif(data["program"]=="ME"):
				temp=temp+"Mechanical Engineering"
			elif(data["program"]=="Biotech"):
				temp=temp+"Biotechnology"
			elif(data["program"]=="CSE"):
				temp=temp+"Computer Science & Engineering"
			elif(data["program"]=="ECE"):
				temp=temp+"Electronics & Communication Engineering"
			elif(data["program"]=="EEE"):
				temp=temp+"Electrical & Electronics Engineering"
			if(w_count==0):
				w=w+" program like \'" + temp +"\'"
				w_count=w_count+1
				
			else:
				w=w+" AND " + " program like \'" + temp + "\'"
		if(data["enrolment_id"]==""):
			if(c_count==0):
				c=c+"enrolment_id"
				c_count+=1
			else:
				c=c+" , "+ "enrolment_id"
		elif(data["enrolment_id"]!="No"):
			if(w_count==0):
				w=w+" enrolment_id = " + data["enrolment_id"]
				w_count=w_count+1
			else:
				w=w+" AND " + " enrolment_id = " + data["enrolment_id"]
		if(data["phone"]==""):
			if(c_count==0):
				c=c+"phone"
				c_count+=1
			else:
				c=c+" , "+ "phone"
		elif(data["phone"]!="No"):
			if(w_count==0):
				w=w+" phone like \'" + data["phone"]+"\'"
				w_count=w_count+1
			else:
				w=w+" AND " + " phone like \'" + data["phone"]+"\'"
		if(data["year"]==""):
			if(c_count==0):
				c=c+"year"
				c_count+=1
			else:
				c=c+" , "+ "year"
		elif(data["year"]!="No"):
			if(w_count==0):
				w=w+" year = " + data["year"]
				w_count=w_count+1
			else:
				w=w+" AND " + " year = " + data["year"]
		
		"""if(data["password"]=="y"):
									if(c_count==0):
										c=c+"password"
										c_count=c_count+1
									else:
										c=c+" , "+"password"""

		print(c,'\n',w)
		if(c=="" and w==""):
			return "khaali"
		elif(c==""):
			c="*"
		query=""
		if(w==""):
			query="select " + c + " from student"
			ct.execute(query)
		else:
			query="select " + c + " from student where " + w
			ct.execute(query)
		conn.commit()
		print("Ye query hai "+query)
		print("Aur ye hai uska output")
		ct=list(ct)	# output of the query in the list
		print(ct)
		c=c.split(',')
		c=list(map(lambda x:x.upper(),c))
		return render_template('result.html',data=ct,heading=c)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/courses')
def courses():
	return render_template('courses.html')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/teacher')
def teacher():
	return render_template('teacher.html')

@app.route('/pollsList')
def root():
	conn = sqlite3.connect('KM.db')
	c=conn.cursor()
	c.execute("select count(*) from poll;")
	c=list(c)
	return render_template('pollsList.html' , count=c[0][0])

@app.route('/poll/<poll_id>')
def poll(poll_id):
	poll_data={}
	vote = request.args.get('field')
	conn = sqlite3.connect('KM.db')
	c=conn.cursor()
	c.execute('select question from poll where poll_id='+poll_id+';')
	poll_data['question']=list(c)[0][0]
	c.execute('select data from poll_data where poll_id='+poll_id+';')
	poll_data['fields']=list(map(lambda x:x[0],list(c)))
	#print(render_template('poll.html' , data=poll_data))
	if vote:
		print("here")
		c.execute("update poll_data SET count=count+1 where poll_id="+poll_id+" and data='"+vote+"';")
		conn.commit()
		return render_template('thankyou.html', data=poll_data)
	else:
		return render_template('poll.html' , data=poll_data,poll_id=poll_id)
	
@app.route('/resultList')
def res():
	conn = sqlite3.connect('KM.db')
	c=conn.cursor()
	c.execute("select count(*) from poll;")
	c=list(c)
	return render_template('resultList.html' , count=c[0][0])

@app.route('/results/<poll_id>')
def show_results(poll_id):
	votes = {}
	poll_data={}
	conn = sqlite3.connect('KM.db')
	c=conn.cursor()
	c.execute('select question from poll where poll_id='+poll_id+';')
	poll_data['question']=list(c)[0][0]
	c.execute('select data from poll_data where poll_id='+poll_id+';')
	poll_data['fields']=list(map(lambda x:x[0],list(c)))
	c.execute('select data,count from poll_data where poll_id='+poll_id+';')
	#print(list(map(lambda x:x[0],list(c))))
	datass=[]
	valuees=[]
	for i in list(c):
		datass.append(i[0])
		valuees.append(i[1])
	#datass=list(map(lambda x:x[0],list(c)))
	#valuees=list(map(lambda x:x[1],list(c)))
	print(datass,valuees)
	for i,j in zip(datass,valuees):
		votes[i]=j
	print(votes)
	return render_template('results.html', data=poll_data, votes=votes,poll_id=poll_id)

if __name__=="__main__":
	app.run(port=5678,debug=True)
