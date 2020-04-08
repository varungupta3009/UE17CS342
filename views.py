from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import random
import re

app=Flask(__name__)
app.secret_key = "abc"
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
            c.execute("insert into lecture values('"+data['emailId']+"','"+data['name']+"','"+data['branch']+"','"+data['password']+"','"+data['phone']+"','"+data['gender']+"');")
            conn.commit()
            return redirect('/signin')
        except Exception as e:
        	print(e)
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
		if(len(list(c))==0):
			return render_template("student.html",msg="Student Does not exist")
		else:
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
        elif(len(d)>0):
        	e=d
        else:
        	return render_template('signin.html',data="Username and password does not match")    
        session['emailId']=data['emailId']
        msg="SignIn Successfull"
        return "SignedIn"

@app.route('/signout')
def signout():
	if 'emailId' in session:
		del session['emailId']
		return redirect('/')
	else:
		abort(400)

@app.route('/brainstorm', methods=['GET','POST','DELETE'])
def brainstorm():
	conn = sqlite3.connect('KM.db')
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
		return render_template('blog.html',data=l)
	else:
		c=conn.cursor()
		c.execute("select * from blog;")
		c=list(c)
		return render_template('blog.html',data=c)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
	conn = sqlite3.connect('KM.db')
	if request.method=="GET":
		if 'emailId' in session:
				return render_template('newpost.html')
		else:
			return redirect('/signin')
	elif request.method=="POST":
		data=request.form
		date=str(datetime.now())
		c=conn.cursor()
		c.execute("insert into blog(posted_by,heading,datetime,post) values('"+session['emailId']+"','"+data['heading']+"','"+date+"','"+data['post']+"');")
		conn.commit()
		c.execute("select post_id from blog where posted_by='"+session['emailId']+"' and heading='"+data['heading']+"';")
		post_id=list(c)[0][0]
		hashtags1=re.findall(r"#(\w+)", data['post'])
		hashtags2=re.findall(r"#(\w+)", data['hashtags'])
		hashtag=hashtags1+hashtags2
		print(post_id,hashtag)
		for i in hashtag:
			try:
				print(type(post_id),type(i))
				c.execute("insert into hashtag(post_id,hashtag) values("+str(post_id)+",'"+i+"');")
			except Exception as e:
				print("hastag reused",e)
		conn.commit()
		return redirect('/blog')

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
		
		if(data["password"]=="y"):
			if(c_count==0):
				c=c+"password"
				c_count=c_count+1
			else:
				c=c+" , "+"password"

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
		return "Check terminal Output"
		
if __name__=="__main__":
	app.run(port=5678,debug=True)
