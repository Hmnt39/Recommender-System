# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 15:24:56 2017

@author: Hemant Mishra
""" 

from wtforms import Form,BooleanField,TextField,PasswordField,validators
from passlib.hash import sha256_crypt
from new import create_model,popular
import gc
import sqlite3 as sql
from functools import wraps
from flask import Flask,render_template,redirect,request,url_for,session,g


app=Flask(__name__)
app.secret_key="recommendation"

@app.before_request
def before_request():
    g.db = sql.connect("recommender.db")
    
    
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()
        
conn=sql.connect('data.db')
conn.text_factory=str
cur=conn.cursor()

       
@app.route("/")
def main():
    l=popular(cur)
    return render_template('index.html',l=l)


def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('main'))


anime=[]
rating=[]
@app.route("/dashboard/")
def dashboard():
    if session['logged_in']==True: 
        name=session['username']
        x=len(anime)
        return render_template('dashboard.html', name=name,x=x)

@app.route("/dashboard/result/",methods=['GET','POST'])
def result():
    if session['logged_in']==True:
        if request.method=="POST":
            query = "%" + request.form['show'] + "%"
            if cur.execute("select name,anime_id from anime where name like ?",[query]):
                data=cur.fetchall()
            else:
                data=[]
            return render_template('result.html',d=data)

@app.route("/dashboard/receiver/",methods=['POST','GET'])
def receiver():
    if request.method=="POST":
        data=request.form['btn']
        anime.append(int(data))
        cur.execute("select rating from anime where anime_id =(?)",[data])
        r=cur.fetchone()
        rating.append(r[0])
        return redirect(url_for("dashboard"))
        
@app.route("/dashboard/final/",methods=['POST','GET'])
def final():
    if session['logged_in']==True:
        data=create_model(anime,rating,cur)
        anime[:]=[]
        rating[:]=[]
        return render_template('final.html',d=data)
    
        
@app.errorhandler(404)
def err404(e):
    return render_template('404.html')

@app.errorhandler(500)
def err500(e):
    return render_template('500.html')

@app.route("/login/", methods=['GET','POST'])
def login():
    error=""
    try:
        if request.method=="POST":     
            data=g.db.execute("SELECT * FROM user1 WHERE username = (?)",
                           [request.form['username']]).fetchone()
            if len(data)==0:
                error="Invalid Credentials.Try Again!!"
            data=data[2]
            if sha256_crypt.verify(request.form['password'],data):
                session['logged_in']=True
                session['username']=request.form['username']
                session['password']=data
                return redirect(url_for("dashboard"))
            
            else:
                error="Invalid credentials. Try Again!!" 
        gc.collect()
        return render_template('login.html',error=error)
    except Exception as error:
        return render_template('login.html',error=error)
    
    
class Registrationform(Form):
    fname=TextField('<strong style="color:white;">FIRST NAME</strong>',[validators.Length(min=4,max=20)])
    lname=TextField('<strong style="color:white;">LAST NAME</strong>',[validators.Length(min=4,max=20)])
    username=TextField('<strong style="color:white;">USERNAME</strong>',[validators.Length(min=4,max=20)])
    email=TextField('<strong style="color:white;">EMAIL ADDRESS</strong>',[validators.Length(min=6,max=40)])
    password=PasswordField('<strong style="color:white;">PASSWORD</strong>',[validators.DataRequired(),validators.EqualTo('confirm',message="Password must match")])
    confirm=PasswordField('<strong style="color:white;">REPEAT PASSWORD</strong>')
    accept_tos=BooleanField('<small style="color:white;">By clicking Register, you agree to the <a href="#" data-toggle="modal" data-target="#t_and_c_m">Terms and Conditions</a></small> ',[validators.DataRequired()])
    
    
    

@app.route("/register/", methods=["GET","POST"])
def register():
    try:
        form = Registrationform(request.form)
        if request.method=="POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.hash((str(form.password.data)))
            
            x = g.db.execute("SELECT * FROM user1 WHERE username = (?)",
                          [username]).fetchall()
            print(x)
            if len(x)>0:
                return render_template('register.html',form=form)
            else:
                g.db.execute("INSERT INTO user1 (username,password,email) VALUES (?,?,?)",
                          (username,password,email))
                g.db.commit()                
                gc.collect()
                session['logged_in']=True
                session['username']=username
                return redirect(url_for('login'))
        return render_template('register.html',form=form)
    except Exception as e:
        return(str(e))

if __name__ == "__main__":
    app.run()    