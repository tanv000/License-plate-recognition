from flask import Flask,render_template,request,flash,jsonify
from flask_mail import Mail,Message
import os
import json
import time
from predict import OCR
from pymongo import MongoClient
from flask_cors import CORS 
import uuid
import random
from PIL import Image
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity

# mongoDb connection
client=MongoClient("mongodb://localhost:27017")
# database name
db=client['Challan_System']
# collections in the db
ccv=db['Vehical_info']
ccc=db['Challen_Raised']
ccl=db['authority_login']

app=Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='challansystemalpr@gmail.com'
app.config['MAIL_PASSWORD']='onkbcoonzjzbummd'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
app.config['JWT_SECRET_KEY']='hdcbfvgffbcvmegkyuc3v5259gbvhyfc7921'
jwt=JWTManager(app)
mail=Mail(app)
app.secret_key="super secret key"
BASE_PATH=os.getcwd()
UPLOAD_PATH=os.path.join(BASE_PATH,'frontend/public/assets/upload')

@app.after_request
def add_cors_headers(response):
      response.headers['Access-Control-Allow-Origin']='http://localhost:3000'
      response.headers['Access-Control-Allow-Headers']='Content-Type'
      return response

@app.route('/demologin',methods=['POST'])
def demo():
      data=request.get_json()
      print(data.get('username'))
      return jsonify({'success':'success'})

@app.route('/login',methods=['POST'])
def login():
      data=request.get_json()
      print(data)
      username=data.get('username')
      password=data.get('password')
      y=None
      x=ccl.find_one({'username':username})
      if(type(x)!=type(y)):
            y=dict(x)
            actpass=y['password']
            if(password==actpass):
                  access_token=create_access_token(identity=username)
                  ccl.update_one({'username':username},{'$set':{'tokens.token':[access_token]}},upsert=True)
                  return jsonify({'access_token':access_token,'status':200}),200
            else:
                  return jsonify({'error':'invalid password','status':401}),401
      else:
            return jsonify({'error':'invalid username','status':402}),402

@app.route('/upload',methods=['POST'])
def indexnative():
        # detectn=[]
        upload_file=request.files['image']
        # image=Image.open(upload_file).convert('RGB')
        filename=f"{str(uuid.uuid4())}.jpg"
        path_save=os.path.join(UPLOAD_PATH,filename)
        upload_file.save(path_save)
        text=[]
        text=(OCR(path_save,filename))
        n=len(text)
        return ({
             "upload_image":filename,
             "output":text,
             "detectno":n})

@app.route('/protected',methods=['GET'])
@jwt_required()
def protected():
      current_user=get_jwt_identity()
      print(current_user)
      return jsonify({'name':current_user,'status':200})

@app.route('/detect',methods=['POST','GET'])
def index():
    if request.method=='POST':
        upload_file=request.files['image_name']
        filename=f"{str(uuid.uuid4())}.jpg"
        path_save=os.path.join(UPLOAD_PATH,filename)
        upload_file.save(path_save)
      #   path_save1=os.path.join(UPLOAD_PATH1,filename)
      #   upload_file.save(path_save1)
        text=(OCR(path_save,filename))
        n=len(text)
        return render_template('index.html',upload=True,upload_image=filename,total=n,output=text)
    return render_template('index.html',upload=False)

@app.route('/register',methods=['POST'])
def register():
        try:
                data=request.get_json()
                name=data.get('ownername')
                vehicalnumber=data.get('vehicalno')
                phoneNumber=data.get('phoneno')
                address=data.get('address')
                email=data.get('email')
                registered_by=data.get('registedred_by')
                ccv.insert_one({'lc_number':vehicalnumber,
                                'name':name,
                                'phoneno':phoneNumber,
                                'address':address,
                                'email':email,
                                'registered_by':registered_by,
                                })
                return jsonify({'status':200})
        except Exception as e:
               return jsonify({'status' :422})
@app.route('/raisechallan',methods=['POST'])
def raisechallan():
        data=request.get_json()
        lc_number=data.get('vehicalno')
        offence=data.get('offence')
        proof=data.get('offence_proof')
        booked_by=data.get('challan_booked_by')
        current_time=datetime.datetime.now()
        y=None
        x=ccv.find_one({'lc_number':lc_number})
        if(type(x)!=type(y)):
              y=dict(x)
              receiver_email=y['email']
              ccc.insert_one({
                    'lc_number':lc_number,
                    'ownername':y['name'],
                    'email':y['email'],
                    'offence':offence,
                    'datetime_of_offence':current_time,
                    'proof':proof,
                    'Challan_booked_by':booked_by,

              })
            
              msg=Message('Challan on your vehical no:'+lc_number,sender='challansystemalpr@gmail.com',recipients=[receiver_email])
              msg.body='challan has been raised on your vehical no: '+lc_number+' due to '+offence+' on the owner of the vehical '+y['name']+' on '+str(current_time)+' pay your challan before the due date i.e '+str(current_time+datetime.timedelta(days=15))
              mail.send(msg)
              return jsonify({'status':200}),200
        else:
              return jsonify({'status':422}),422
if __name__=='__main__':
    app.run(host='192.168.6.60',debug=True)
    