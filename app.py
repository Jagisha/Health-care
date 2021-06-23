#app.py
from flask import Flask,request, url_for, redirect, render_template, jsonify,session
import sqlite3 as sql
from flask_cors import CORS, cross_origin
import pickle
import numpy as np
import os
import pandas as pd
import csv
#from sklearn.externals import joblib
#import sklearn.external.joblib as extjoblib
import joblib
from sklearn.preprocessing import StandardScaler




app = Flask(__name__)
app.secret_key = "Secret Key"
# load the saved model file and use for prediction
logit_model = joblib.load('rf_model.pkl')

logit_model_diabetes = joblib.load('dt_model_diabetes.pkl')
logit_model_bmi=joblib.load(open('clf.pkl','rb'))
model = pickle.load(open('model.pkl', 'rb'))
scaler = pickle.load(open('scaler.pkl', 'rb'))
model1=pickle.load(open('knnmodel.pkl','rb'))




@app.after_request # blueprint can also be app~~
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


# ==================================
#  Insert data in database (SIGNUP)
# ==================================
def insertUser(username, email, password, contact):
    con = sql.connect("test.db")
    cur = con.cursor()
    phone = int(contact)
    query = ("""INSERT INTO USERS
             (username,email,password,contact)
             VALUES ('%s','%s','%s',%d)""" %
             (username, email, password, phone))
    cur.execute(query)
    con.commit()
    con.close()


# =====================================
#  Validating data in database (LOGIN)
# =====================================
def validUser(email, password):
    con = sql.connect("test.db")
    cur = con.cursor()
    query = ("""SELECT * FROM USERS
             where email = '%s' and password = '%s'
             """ %
             (email, password))
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    return data


# ===================
#    Flask Routing
# ===================

@app.route('/')
def home111():
    return render_template('login_1.html')

# Login page
@app.route('/signin/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        rd = validUser(request.form['email'], request.form['password'])
        if rd:
            session['user']=rd[0] 
            return render_template('homepage_1.html')
        else:
            msg="Wrong username or password"
            return render_template('login_1.html',msg=msg)
    else:
        return render_template('login_1.html')
        
        
# ===================
#    Flask Logout
# ===================
@app.route('/signin/logout')
def logout():
	session.pop('user', None)
	return render_template('login_1.html')
    
# ===================
#    Flask Logout2
# ===================    
@app.route('/logout')
def logout1():
	session.pop('user', None)
	return render_template('login_1.html')
    
# ===================
#   Check session 
# is active or not
# ===================    
@app.route('/s')
def student():
    if 'user' in session:  
        s = session['user']
        all_data = Student.query.all()  
        return render_template("homepage_1.html", all_data = all_data,user=s)
    else:   
        return render_template('login_1.html')


# ===================
#  signup page
# ===================
@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        insertUser(username, email, password, contact)
        msg= "account created successfully"
        return redirect(url_for('login'))
    else:
        return render_template('login_1.html')

# api json 
@app.route('/sum', methods=['GET','POST'])
def sum():
    sum = 0
    a = int(request.args.get('a'))
    b = int(request.args.get('b'))
    sum = a+b
    return jsonify(sum)

# ===================
#   Main Page
# ===================
@app.route('/mainpage')
def mainhome():
    return render_template("homepage_1.html")

# ===================
#   Contact Us Page
# ===================
@app.route('/demo')
def contact():
    return render_template("contact_me.html")
    

# ===================
#   Backend Heart Page
# ===================
@app.route('/backend')    
def data124(): 
    return render_template("backheart.html")  

    
    
    
# ===================
#   Heart Disease Page
# ===================    
@app.route('/heart')
def home1():
    return render_template("heart.html")
# Always at end of file !Important!

@app.route('/heart/predict',methods=['POST','GET'])
def predict1():
    # receive the values send by user in three text boxes thru request object -> requesst.form.values()
    
    int_features = [float(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    print(final_features)
       
    prediction1=logit_model.predict(final_features)
    if prediction1 == 1:
        pred = "You have Heart Disease, please consult a Doctor."
    elif prediction1 == 0:
        pred = "You don't have Heart Disease."
    output = pred
   
    return render_template('heart.html', pred= '{}'.format(output))

@app.route('/heartdata')
def data():
	df=pd.read_csv("https://raw.githubusercontent.com/anmol2806/Python_practice1/main/Csv%20files/heart.csv")
	data_table=df.to_html()
	filepath = os.path.join('/Users/hp/Documents/Github/aimlproject/templates', 'heartdata.html')
	text_file = open(filepath, "w")
	text_file.write(data_table)
	text_file.close()
	return render_template("heartdata.html")  
    
@app.route('/backheartdata')    
def data123(): 
    return render_template("backheart.html")  
    
    
    
# ===================
#   Diabetes Page
# ===================    
@app.route('/diabetes')
def home2():
    return render_template('diabetes.html')  

@app.route('/diabetes/predict',methods=['POST'])
def predict2():
    '''
    For rendering results on HTML GUI
    '''
    float_features = [float(x) for x in request.form.values()]
    final_features1 = [np.array(float_features)]
    prediction2 = logit_model_diabetes.predict(final_features1 )

    if prediction2 == 1:
        pred = "You have Diabetes, please consult a Doctor."
    elif prediction2 == 0:
        pred = "You don't have Diabetes."
    output = pred

    return render_template('diabetes.html', prediction_text='{}'.format(output))
    
@app.route('/backdiabetesdata')    
def data125(): 
    return render_template("backdiabetes.html")  
    



# ===================
#  BMI Page
# ===================
@app.route('/bmi')
def home3():
    return render_template("bmi.html")


@app.route('/bmi/predict',methods=['POST','GET'])
def predict3():
    int_features = [int(x) for x in request.form.values()]
    y=int_features[2]/(int_features[1]*0.0254)**2
    int_features.append(y)
    final_features = [np.array(int_features)]
    prediction=logit_model_bmi.predict(final_features)
    
    return render_template('bmi.html', pred=prediction)

@app.route('/backendbmidata')    
def data126(): 
    return render_template("backbmi.html")  




# ===================
#   Heart Failure Page
# ===================
@app.route('/hfa')
def hfa():
    return render_template("heart_fail.html")


@app.route('/predicthfa',methods=['POST'])
def predicthfa():

    features = [float(x) for x in request.form.values()]
    final_features = [np.array(features)]
     
    prediction = model.predict(final_features)
    
    if prediction == 1:
        pred = "THE PATIENT IS LIKELY TO HAVE A HEART FAILURE"
    elif prediction == 0:
        pred = "THE PATIENT IS NOT LIKELY TO HAVE A HEART FAILURE"
    output = pred

    '''print("final features",final_features)
    print("prediction:",prediction)
    output = round(prediction[0], 2)
    print(output)'''
    return render_template('heart_fail.html', prediction_text='{}'.format(output))
    '''if output == 0:
        return render_template('heart_pred.html', prediction_text='THE PATIENT IS NOT LIKELY TO HAVE A HEART FAILURE')
    else:
         return render_template('heart_pred.html', prediction_text='THE PATIENT IS LIKELY TO HAVE A HEART FAILURE')
        '''
        
@app.route('/predict_api',methods=['POST'])
def results():

    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)



@app.route('/hprob')
def home():
    return render_template("heart_prob.html")

@app.route('/hprob/predict',methods=['POST','GET'])
def predict():
    # receive the values send by user in three text boxes thru request object -> requesst.form.values()
    
	int_features = [int(x) for x in request.form.values()]
	final_features = [np.array(int_features)]
	
	#print(final_features)
	
	#final_features =  [[52 , 2,  168, 76, 120, 80, 1,  0,  1, 4]] 
	#[[48,	2,	169,	82,	150,	100,	0,	0,	1, 4	]]   
	
	prediction=model1.predict_proba(final_features)
	output='{0:.{1}f}'.format(prediction[0][1], 2)
   
	return render_template('heart_prob.html', pred='Heart Disease probability is :  {}'.format(output))
	#return render_template('index.html', pred= final_features) 
 
 



 
if __name__== '__main__':
    app.run(debug=True)
    