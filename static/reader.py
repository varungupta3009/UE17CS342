import csv
import sqlite3
conn=sqlite3.connect('../KM.db')
c=conn.cursor()
with open('2.1 Students admission year wise.csv') as f:
	f1=csv.DictReader(f)
	for row in f1:
		name=row['Name of the student']
		gender=row['Gender']
		srn=row['Student ID  number']
		email=row['Email ID']
		program=row['Program name']
		enr=row['Enrolment ID']
		mob=row['Mobile Number']
		year=row['Year of joining']
		try:
			c.execute("insert into student values('"+name+"','"+gender+"','"+srn+"','"+email+"','"+program+"','"+enr+"','"+mob+"',"+year+",'');")
		except Exception as e:
			print(e)
conn.commit()