from flask import Flask,render_template, request,session
import mysql.connector
import pickle
import numpy as np

app=Flask(__name__)
app.secret_key = "your key"

db_connection=mysql.connector.connect(
    host='localhost',
    user='root',
    password="",
    database='pcancer'
)
db_cursor=db_connection.cursor()

with open('model.pkl','rb') as file:
    
    model=pickle.load(file)

@app.route("/")
def home():
    return render_template("main.html")

@app.route("/userreg",methods=['GET','POST'])
def regsiter():
    if request.method=='POST':
        name=request.form['fullname']
        email=request.form['email']
        phn=request.form['mobilenumber']
        password=request.form['password']
        db_cursor.execute('Insert into user(name,email,phone,password) values (%s,%s,%s,%s)',(name,email,phn,password))
        db_connection.commit()
        return render_template('login.html')
    return render_template("reg.html")

@app.route('/userlogin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db_cursor.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
        user = db_cursor.fetchone()
        if user:
            session['user']=email
            return render_template('homepage.html')
    return render_template('login.html')

@app.route('/test', methods=['GET','POST'])
def test():
    if request.method=="POST":
        email=session['user']
        name = request.form['name'] 
        age = request.form['age']
        gender = request.form['gender']
        session['sex']=gender
        date = request.form['date']
        diagnosis = request.form['diagnosis']
        lyve1 = request.form['lyve1']
        tff1 = request.form['tff1']
        reg1b = request.form['reg1b']
        plasma_CA19_9 = request.form['plasma_CA19_9']
        REG1A = request.form['REG1A']
        if gender == "Male" or gender == "male":
            gender=1 
        else:
            gender=0
        input_data = [[age, gender, plasma_CA19_9, diagnosis, lyve1, reg1b, tff1, REG1A]]
        input_data = [float(i) for i in input_data[0]]
        input_data = np.array(input_data).reshape(1, -1) 
        print( input_data )
        prediction=model.predict(input_data)
        if prediction == 0:
            result = "You are healthy,Continue with your healthy lifestyle choices"
        elif prediction == 1:
            result = "Mild Be cautious, look out for your health, exercise and eat right"
        else:
            result = "It's Severe Consult the doctor as soon as possible"
        print(result)
        sex=session['sex']
        db_cursor.execute('Insert into health_form (name, age, gender ,date, diagnosis, lyve1, tff1, reg1b, plasma_CA19_9, REG1A, result, email) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)',(name, age, sex ,date, diagnosis, lyve1, tff1, reg1b, plasma_CA19_9, REG1A,result,email))
        db_connection.commit()
        return render_template('form.html',r=result)
    return render_template('form.html')
from datetime import datetime
@app.route('/data')
def data():
    if 'user' in session:
        email = session['user']
        db_cursor.execute('SELECT name, age, gender ,date, diagnosis, lyve1, tff1, reg1b, plasma_CA19_9, REG1A, result FROM health_form WHERE email=%s', (email,))
        rows = db_cursor.fetchall()  # This will fetch all rows where the condition matches

        formatted_rows = []
        for row in rows:
            # Assuming the fourth element in each row is a datetime object
            if isinstance(row[3], datetime):
                formatted_row = row[:3] + (row[3].strftime("%Y-%m-%d"),) + row[4:]
            else:
                formatted_row = row
            formatted_rows.append(formatted_row)

        return render_template("reports.html", data=formatted_rows)


@app.route('/homepage')
def homepage():
    if session['user']:
        return render_template("homepage.html")
        


@app.route('/logout')   
def logout():
    session.pop('user', None)
    return render_template("main.html")

if __name__=='__main__':
    app.run(debug=True)