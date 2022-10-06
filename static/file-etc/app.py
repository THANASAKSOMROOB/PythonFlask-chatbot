from ast import Return
from distutils.debug import DEBUG
from email import message
import re
from tabnanny import verbose 
import time
from flask import Flask, request, abort, jsonify, render_template, redirect
import requests
import json
import random
from sklearn.metrics import accuracy_score, precision_score, recall_score
import tflearn
import numpy
import nltk
import pickle
from tensorflow.python.framework import ops
from nltk.stem.lancaster import LancasterStemmer
from linebot import LineBotApi
import PIL.Image as Image
import io
import os
from linebot.models import (
    LocationSendMessage, TextSendMessage, QuickReply, QuickReplyButton, LocationAction, CameraAction, FlexSendMessage)
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords
import datetime
from math import cos, asin, sqrt
#database
import sys
import pyodbc as odbc
#gen id
import uuid

#ของฝนลองเอาเทส
""" from Project.imageclass.city2 import classified """

# ถ้ามีเวลาเหลือ ทำที่แอดคำใหม่เข้าไปด้วย จากฝั่ง admins
# แล้วถ้าเจอคำใหม่ๆที่ไม่อยู่ใน dataset เลย แต่ความหมายมันลื่อในปัญหานั้น จะทำยังไงให้มันรู้

# data base config
DRIVER = 'SQL Server'
SERVER_NAME = 'DESKTOP-411SBKC\SQLEXPRESS'
DATABASE_NAME = 'Datachatbot'
username = 'sa' 
password = 'P@ssw0rd' 

conn_string = f"""
    Driver={{{DRIVER}}};
    Server={SERVER_NAME};
    Database={DATABASE_NAME};
    username={username};
    password={password};
    Trust_Connection=yes;
"""

# ที่อยู่รูปที่บันทึก
dir_path = 'C:/Users/ThanasakSomroob/Desktop/test2/flaskchatbot/flaskchatbot/static/pic'

# ข้อมูล Line developers chatbot
Channel_access_token = 'kDT/5enzQDKjpq4uoMqlR9gMXundmCi1AAalqGVVkiV7oZOwQ0cPWOwT7f2Xoy+td4QJec6AYPiLyMH3HYs0RXYcC82N0qSsLn/SHFoWp1NOyIGNcZ8wAW51d7BZhGLcZ/HBflHCehNf4dJlirS0MQdB04t89/1O/w1cDnyilFU='
Channel_secret = '82e05412afa9c30fe70f7cc2e4637ebc'
basic_id = '@857ebjud'
LINE_API = 'https://api.line.me/v2/bot/message/reply'
line_bot_api = LineBotApi(Channel_access_token)

# run Flask
app = Flask(__name__)
print("name",   app)


# เก็บ state เพื่อให้บอทรู้ว่า เป็น location ของ case ไหน
#state_tag = ""

# webhook ส่งข้อมูลกับ Line


@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    global Problem_type
    if request.method == 'POST':
        # print(request.json)
        dataload = request.json
        print("testdata")
        print(dataload)
        # ทางไลน์ส่งมา
        Reply_token = dataload['events'][0]['replyToken']
        message_type = dataload['events'][0]['message']['type']
        if message_type == 'text':
            message = dataload['events'][0]['message']['text']
            # print(message)
            inp = message
            results = model.predict([bag_of_word(inp, words)])
            results_index = numpy.argmax(results)
            value_predict = results[0][results_index]
            print(results[0])
            print("re", results)
            print("max", results_index)
            print("max value", results[0][results_index])
            print(labels)
            if (float(value_predict) < 0.7):
                TextMessage = "ผมไม่เข้าใจกรุณาส่งข้อความอีกครั้งครับ"
                sendtextunderstand(Reply_token, TextMessage)  
            else:                      
                tag = labels[results_index]
                for tg in data["intents"]:
                    if tg['tag'] == tag:
                        responses = tg['responses']
                        re_m = random.choices(responses)
                        Reply_message = ' '.join([str(elem) for elem in re_m])
                        print("คำตอบ", Reply_message)
                        date = datetime.datetime.now()
                        if tg['tag'] == "greeting":
                            greeting(Reply_token, Reply_message)
                            # ReplyMessage(Reply_token,Reply_message,Channel_access_token,message_type)
                        elif tg['tag'] == "flood problem":
                            state_tag = "flood problem"
                            data_tag = {
                                        "data_tag":{
                                                "State_tag":"{}".format(state_tag),
                                                "date":"{}".format(date.strftime("%m/%d/%Y")),
                                                "Time":"{}".format(date.strftime("%H:%M:%S"))}}
                            with open('static/file-etc/state_tag.json', 'w') as f:
                                json.dump(data_tag, f)
                            Camera_Action(Reply_token, Reply_message)
                        elif tg['tag'] == "road problem":
                            state_tag = "road problem"
                            data_tag = {
                                        "data_tag":{
                                                "State_tag":"{}".format(state_tag),
                                                "date":"{}".format(date.strftime("%m/%d/%Y")),
                                                "Time":"{}".format(date.strftime("%H:%M:%S"))}}
                            with open('static/file-etc/state_tag.json', 'w') as f:
                                json.dump(data_tag, f)
                            Camera_Action(Reply_token, Reply_message)
                        elif tg['tag'] == "electrical problem":
                            state_tag = "electrical problem"
                            data_tag = {
                                        "data_tag":{
                                                "State_tag":"{}".format(state_tag),
                                                "date":"{}".format(date.strftime("%m/%d/%Y")),
                                                "Time":"{}".format(date.strftime("%H:%M:%S"))}}
                            with open('static/file-etc/state_tag.json', 'w') as f:
                                json.dump(data_tag, f)
                            Camera_Action(Reply_token, Reply_message)
                        elif tg['tag'] == "garbage problem":
                            state_tag = "garbage problem"
                            data_tag = {
                                        "data_tag":{
                                                "State_tag":"{}".format(state_tag),
                                                "date":"{}".format(date.strftime("%m/%d/%Y")),
                                                "Time":"{}".format(date.strftime("%H:%M:%S"))}}
                            with open('static/file-etc/state_tag.json', 'w') as f:
                                json.dump(data_tag, f)
                            Camera_Action(Reply_token, Reply_message)
                        elif tg['tag'] == "drought_problem":
                            state_tag = "drought_problem"
                            data_tag = {
                                        "data_tag":{
                                                "State_tag":"{}".format(state_tag),
                                                "date":"{}".format(date.strftime("%m/%d/%Y")),
                                                "Time":"{}".format(date.strftime("%H:%M:%S"))}}
                            with open('static/file-etc/state_tag.json', 'w') as f:
                                json.dump(data_tag, f)
                            Camera_Action(Reply_token, Reply_message)    
                        elif tg['tag'] == "no_picture":
                            state_tag = "no_picture"
                            data_tag = {
                                        "data_tag":{
                                                "State_tag":"{}".format(state_tag),
                                                "date":"{}".format(date.strftime("%m/%d/%Y")),
                                                "Time":"{}".format(date.strftime("%H:%M:%S"))}}
                            with open('static/file-etc/state_tag.json', 'w') as f:
                                json.dump(data_tag, f)
                            Quick_Reply(Reply_token)
                        #elif tg['tag'] == "track_problems":
                            # ยังติดปัญหาว่าจะเอาหมายเลขที่ส่งมาออกมาใช้ยังไง
                            #sendtextunderstand(Reply_token, Reply_message)
                        elif tg['tag'] == "PM2.5":
                            state_tag = "PM2.5"
                            data_tag = {
                                        "data_tag":{
                                                "State_tag":"{}".format(state_tag),
                                                "date":"{}".format(date.strftime("%m/%d/%Y")),
                                                "Time":"{}".format(date.strftime("%H:%M:%S"))}}
                            with open('static/file-etc/state_tag.json', 'w') as f:
                                json.dump(data_tag, f)
                            print(state_tag)
                            #responses = tg['responses']
                            #re_m = random.choices(responses)
                            #Reply_message = ' '.join([str(elem) for elem in re_m])
                            Quick_Reply_PM(Reply_token, Reply_message)
                        elif tg['tag'] == "feedback":
                            state_tag = "feedback"
                            data_tag = {
                                        "data_tag":{
                                                "State_tag":"{}".format(state_tag),
                                                "date":"{}".format(date.strftime("%m/%d/%Y")),
                                                "Time":"{}".format(date.strftime("%H:%M:%S"))}}
                            with open('static/file-etc/state_tag.json', 'w') as f:
                                json.dump(data_tag, f)
                            print(state_tag)
                            feedback(Reply_token, Reply_message)    

            
            """ print(tag)
            print(results_index)
            print(Reply_message)
            ReplyMessage(Reply_token, Reply_message,
                         Channel_access_token, message_type) """
        elif message_type == 'location':
            with open("static/file-etc/state_tag.json", encoding="utf-8") as file:
                data_state_tag = json.load(file)    
                for dst in data_state_tag.values():
                    state_tag = dst['State_tag']
                if (state_tag == "PM2.5"):
                    # api air4thai
                    air4thai_API = requests.get(
                        'http://air4thai.pcd.go.th/services/getNewAQI_JSON.php?')
                    data_api = air4thai_API.text
                    #d_api = json.loads(data_api)
                    data_location = dataload['events'][0]['message']['address']
                    lat = '{}'.format(dataload['events'][0]['message']['latitude'])
                    long = '{}'.format(dataload['events'][0]['message']['longitude'])
                    #std = '{}'.format(dataload['events'][0]['message']['stationID'])
                    print('lat'+lat)
                    print('long'+long)
                    f = open('static/file-etc/dataapi.json')
                    dataapi = json.load(f)
                    # ทำเพื่อค่า stationID     stationID ก็คือเครื่องวัด PM2.5 ใน air4thai
                    # สูตร Haversine formula
                    # 12742 รัศมีของโลก
                    def distance(lat1, long1, lat2, long2):
                        p = 0.017453292519943295 # Math.PI/180
                        hav = 0.5 - cos((float(lat2)-float(lat1))*p)/2 + cos(float(lat1)*p)*cos(float(lat2)*p) * (1-cos((float(long2)-float(long1))*p)) / 2
                        return 12742 * asin(sqrt(hav))

                    def closest(data, v):
                        return min(data, key=lambda p: distance(v['lat'],v['long'],p['lat'],p['long'])) 

                    lat_long_arr = []
                    for i in dataapi:
                        lat_long_arr.append(i) 
                              
                    v = {'lat': '{}'.format(lat), 'long': '{}'.format(long)}
                    closest(lat_long_arr, v)['stationID']
                    s_id = (closest(lat_long_arr, v)['stationID'])

                    stationID_air4thai_API = requests.get(
                        'http://air4thai.pcd.go.th/services/getNewAQI_JSON.php?stationID={}'.format(s_id))
                    data_res = stationID_air4thai_API.text
                    data_api = json.loads(data_res)
                    print("s_id")
                    print(s_id)
                    print(data_api)
                    for d_api in data_api:
                        Pm25 = data_api['LastUpdate']['PM25']['value'] 
                        unit = data_api['LastUpdate']['PM25']['unit']
                        Date = data_api['LastUpdate']['date']
                        Time = data_api['LastUpdate']['time']
                        Aqi = data_api['LastUpdate']['AQI']['aqi']
                        original_date = datetime.datetime.strptime("{}".format(Date), '%Y-%m-%d')
                        date_time = original_date.strftime("%d/%m/%Y")
                    message_type = dataload['events'][0]['message']['type']
                    #ยืดระดับความรุนแรงตาม AQI ของ เว็บ air4thai
                    if int(Aqi) >= 0 and int(Aqi) <= 25:
                        pm_blue(Pm25, Aqi, data_location, Time,Reply_token, date_time)
                    elif int(Aqi) >= 26 and int(Aqi) <= 50:   
                        pm_green(Pm25, Aqi, data_location, Time,Reply_token, date_time)
                    elif int(Aqi) >= 51 and int(Aqi) <= 100:   
                        pm_yellow(Pm25, Aqi, data_location, Time,Reply_token, date_time)
                    elif int(Aqi) >= 101 and int(Aqi) <= 200:   
                        pm_orange(Pm25, Aqi, data_location, Time,Reply_token, date_time)
                    elif int(Aqi) >= 201:   
                        pm_red(Pm25, Aqi, data_location, Time,Reply_token, date_time)             
                    # clear data in State_tag
                    data_tag = {
                                    "data_tag":{
                                            "State_tag":"{}".format(""),
                                            "date":"{}".format(""),
                                            "Time":"{}".format("")}}
                    with open('static/file-etc/state_tag.json', 'w') as f:
                        json.dump(data_tag, f)            
                    #state_tag == ""
                elif (state_tag == "no_picture"):
                    data_tag = {
                                    "data_tag":{
                                            "State_tag":"{}".format(""),
                                            "date":"{}".format(""),
                                            "Time":"{}".format("")}}
                    with open('static/file-etc/state_tag.json', 'w') as f:
                        json.dump(data_tag, f)
                    date = datetime.datetime.now()
                    Message = date.strftime("%d%m%Y%H%M%S")      
                    message_type = dataload['events'][0]['message']['type']
                    Reply_message = 'ขอบคุณสำหรับปัญหาที่แจ้งมาทางเราจะดำเนินการอย่างเร่งด่วน'
                    ticket_id(Reply_token, Message, Reply_message)
                    #ReplyMessage(Reply_token, Reply_message,Channel_access_token, message_type)
                    
                    
                else:
                    print(state_tag)
                    message_type = dataload['events'][0]['message']['type']
                    Reply_message = 'ขอบคุณสำหรับปัญหาที่แจ้งมาครับ'
                    """
                    try:
                        conn = odbc.connect(conn_string)
                    except Exception as e:
                        print(e)
                        print('task is terminated')
                        sys.exit()
                    else:
                        cursor = conn.cursor()

                    insert_statement =  
                      select top(1) Ticket_id, Datetime, Problem_type from Data_ticket order by Datetime desc
                    cursor.execute(insert_statement)
                    #แก้ต่อพน
                    myresult = cursor.fetchall()"""
                    """ response_API = requests.get('https://c900-2001-fb1-3e-427c-68-c56a-7706-271e.ngrok.io/api/ticketid')
                    Message = response_API.text """
                    
                    # gen ticken
                    #Message = "test"
                    date = datetime.datetime.now()
                    Message = date.strftime("%d%m%Y%H%M%S")  
                    print(Message)
                    #ไปเขียน api
                    #ตรงนี้แก้ต่อ
                    if len(Message) > 0:
                        #print(myresult[0][0])
                        #ticket_id(Reply_token, myresult[0][0], Reply_message)
                        ticket_id(Reply_token, Message, Reply_message)
                    else:
                        TextMessage = "แจ้งปัญญาไม่สำเร็จกรุณาติดต่อเจ้าหน้าที่"
                        caseerror(Reply_token, TextMessage)                                
                    #conn.close()             

        elif message_type == 'image':
            
            if 'imageSet' in dataload['events'][0]['message']:
                isone = False
                total_img = dataload['events'][0]['message']['imageSet']['total']
                Count_image = dataload['events'][0]['message']['imageSet']['total']
                Userid = dataload['events'][0]['source']['userId']
                imageid = dataload['events'][0]['message']['imageSet']['id']
                date = datetime.datetime.now()
                #sql_date_time = date.strftime("%d/%m/%Y %H:%M:%S.%f")
                
            else:
                total_img = 1
                isone = True
                Count_image = "1"
                Userid = dataload['events'][0]['source']['userId']
                #imageid = dataload['events'][0]['message']['imageSet']['id']
                imageid = str(uuid.uuid4())
                date = datetime.datetime.now()
                #sql_date_time = date.strftime("%d/%m/%Y %H:%M:%S.%f")    

            for x in dataload['events']:
                #arr_mid_m = []
                #arr_mid_m.append(x['message']['id'])
                message_id = x['message']['id']
                #save image from Line
                message_contents = line_bot_api.get_message_content(
                    x['message']['id'])
                with open('static/file-etc/file_path', 'wb') as fd:
                    for chunk in message_contents.iter_content(chunk_size=720*720):
                        # ขนาดอันรูปอันก่อน 1024*1024
                        fd.write(chunk)
                with open('static/file-etc/file_path', mode='rb') as file:
                    filepath = file.read()
                    img = Image.open(io.BytesIO(filepath))
                    #dataBytesIO.seek(0)
                    # img.show()
                #print(arr_mid_m)
                filename = 'pic{}.jpg'.format(message_id)
                file_path_save = os.path.join(dir_path, filename)
                img.save(file_path_save)
                

                #save data sql server
                #table Data_image
                records = [[Userid, Count_image, filename, imageid, date]]
                try:
                    conn = odbc.connect(conn_string)
                except Exception as e:
                    print()
                    print('task is terminated')
                    sys.exit()
                else: 
                    cursor = conn.cursor()


                insert_statement = """
                    INSERT INTO Data_image
                    VALUES (?, ?, ?, ?, ?)
                """

                try:
                    for record in records:
                        print(record)
                        cursor.execute(insert_statement, record)        
                except Exception as e:
                    cursor.rollback()
                    print(e)
                    print('บันทึกไม่สำเร็จ')
                else:
                    print('records inserted successfully')
                    cursor.commit()
                    cursor.close()
                finally:
                    if conn == 1:
                        print('connection closed')
                        conn.close()
            

            # มีไวเพื่อล้างข้อมูลในไฟล์ file_path
            with open('static/file-etc/file_path', 'wb') as fd:
                fd.close()

            # location action
            # SELECT Count
            try:
                conn = odbc.connect(conn_string)
            except Exception as e:
                print(e)
                print('task is terminated')
                sys.exit()
            else:
                cursor = conn.cursor()

            insert_statement = """
                SELECT Count(Image_id)as Count_image_id FROM Data_image WHERE Image_id = '{}'
            """.format(imageid)
            cursor.execute(insert_statement)
            myresult = cursor.fetchone() 
            my_result = list(myresult)
            #response_API = requests.get('https://c087-1-4-149-0.ngrok.io/city?filepath=B29A059B985D3BA7C29A703BE06E01542964E2AF33E2CF89F4E9A2E580267CEA')
            imageclassification_API = requests.get('https://d3dd-113-53-150-122.ngrok.io/city?filepath={}'.format(imageid))
            Message_API = imageclassification_API.text
            #เปลี่ยนเป็นของฝน
            #Message_API = 'flood'
            Text_Message = ""
            if str(Message_API) == "potholes":
                Text_Message = "ถนนเป็นหลุมเป็นบ่อ"
            elif str(Message_API) == "flood":
                Text_Message = "น้ำท่วม"   
            elif str(Message_API) == "trash":
                Text_Message = "ขยะ"
            if (int(my_result[0]) == int(total_img)) or ((int(total_img)==1) and isone):
                #Quick_Reply_classification(Reply_token, Text_Message)
                Quick_Reply(Reply_token)
                conn.close() 
                # get มาจาก image classification
                # พรุ่งนี้แก้ตรงนี้ เปลี่ยนค่าพารามิเตอร์
                #response_API = requests.get('https://5d10-1-4-149-0.ngrok.io/city?filepath={}'.format(imageid))
                #Quick_Reply(Reply_token)
                
            #ที่เดิมอยู่ตรงนี้
            #แก้เมื่อ3/17/2022
            #print(Text_Message)
            #response_API = requests.get('https://c900-2001-fb1-3e-427c-68-c56a-7706-271e.ngrok.io/api/ticketid?message_id={}&Text_Message={}'.format(message_id, Text_Message))
            #Message = response_API.text
            #print(Message)

        return request.json, 200
    elif request.method == 'GET':

        return 'this is method GET!! เอาไว้ส่งข้อมูลไปมากับไลน์', 200
    else:
        abort(400)


@app.route('/')
def Hello():
    return 'Hello', 200

@app.route('/feedback', methods=['POST','GET'])
def feedback():
    if request.method == 'GET':
        return render_template('feedback.html')
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]
        date = datetime.datetime.now()
        conn = odbc.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Data_feedback (fb_name, fb_email, fd_message, fd_date) VALUES (?, ?, ?, ?)", name, email, message, date)
        conn.commit()
        conn.close()
        time.sleep(3)
        return redirect('/feedback')
        



#ทดสอบลองเขียน api รอมาเองจากพี่มด
@app.route('/api/ticketid', methods=['POST','GET'])
def ticket():
    # save table data_ticket
    #ประเภท+วันที่+imageidที่ได้จากไลน์
    #Ticket_id = date.strftime("%d%m%Y")+message_id
    message_id = request.args.get('message_id')
    Text_Message = request.args.get('Text_Message')
    date = datetime.datetime.now()
    Ticket_id = date.strftime("%d%m%Y")
    Datetime = date.strftime("%d/%m/%Y %H:%M:%S.%f")  
    records = [[Ticket_id, Datetime, Text_Message ]]
    try:
        conn = odbc.connect(conn_string)
    except Exception as e:
        print(e)
        print('task is terminated')
        sys.exit()
    else:
        cursor = conn.cursor()
    insert_statement = """
        INSERT INTO Data_ticket
        VALUES (?, ?, ?)
    """
    try:
        for record in records:
            print(record)
            cursor.execute(insert_statement, record)        
    except Exception as e:
        cursor.rollback()
        print(e.value)
        print('transaction rolled back')
    else:
        print('บันทึก ticket สำเร็จ')
        cursor.commit()
        cursor.close()
    return Ticket_id



@app.route('/api/chatbot', methods=['POST','GET'])
def chatbot_api():
    if request.method == 'GET':
        #dataload = request.json['message']
        dataload = request.args.get('message')
        print('message')
        print(dataload)
        inp = dataload
        results = model.predict([bag_of_word(inp, words)])
        results_index = numpy.argmax(results)
        tag = labels[results_index]
        for tg in data["intents"]:
            if tg['tag'] == tag:
                responses = tg['responses']
                re_m = random.choices(responses)
                Reply_message = ' '.join([str(elem) for elem in re_m])
    elif request.method == 'POST':
         return 'ทดสอบ', 200   
    return  jsonify({'responses': Reply_message})

def sendtextunderstand(Reply_token, TextMessage):
    line_bot_api.reply_message(
        Reply_token,
        TextSendMessage(text=TextMessage))

def feedback(Reply_token, TextMessage):
    with open("static/file-etc/feedback.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")
    message = FlexSendMessage(
        alt_text="problem", contents=json.loads(bbs))
    messages = [    
        TextSendMessage(text=TextMessage),
        message  
    ]   
    line_bot_api.reply_message(Reply_token, messages)


def caseerror(Reply_token, TextMessage):
    line_bot_api.reply_message(
        Reply_token,
        TextSendMessage(text=TextMessage))        

def ticket_id(Reply_token, TextMessage, Reply_message):
    message = TextSendMessage(text = Reply_message)
    messages = [TextSendMessage(text="รหัสติดตามผลการแจ้งปัญหา"+TextMessage),message]
    line_bot_api.reply_message(Reply_token, messages)
    

#Quick_Reply(Reply_token)
def Quick_Reply_classification(Reply_token, TextMessage):
    message = TextSendMessage(
            text='แชร์ที่อยู่บริเวณนั้นมาหน่อยครับ',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=LocationAction(label="Send location")
                    ),
                ]))
    messages = [TextSendMessage(text=TextMessage+""),message]
    line_bot_api.reply_message(Reply_token, messages)
    
  


def Quick_Reply(Reply_token):
    line_bot_api.reply_message(
        Reply_token,
        TextSendMessage(
            text='แชร์ที่อยู่บริเวณนั้นมาหน่อยครับ',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=LocationAction(label="Send location")
                    ),
                ])))


def Quick_Reply_PM(Reply_token, Reply_message):
    line_bot_api.reply_message(
        Reply_token,
        TextSendMessage(
            text=Reply_message,
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=LocationAction(label="Send location")
                    ),
                ])))


def Camera_Action(Reply_token, TextMessage):
    line_bot_api.reply_message(
        Reply_token,
        TextSendMessage(
            text=TextMessage,
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=CameraAction(label="กล้องถ่ายรูป")
                    )
                ])))


def greeting(Reply_token, TextMessage):
    with open("static/file-etc/bubble_greeting.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")
    message = FlexSendMessage(
        alt_text="problem", contents=json.loads(bbs))
    messages = [    
        message,
        TextSendMessage(text=TextMessage)
    ]   
    line_bot_api.reply_message(Reply_token, messages)


def pm_green(Pm25, Aqi, data_location, Time, Reply_token, formatted_date):
    with open("static/file-etc/pm2.5_green.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(Aqi, Pm25, data_location, formatted_date, Time)
        #Aqi, Pm25, data_location, formatted_date, Time
    message = FlexSendMessage(alt_text="pm2.5_green", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณภาพอากาศตอนนี้ดีครับ")]
    line_bot_api.reply_message(Reply_token, messages)

def pm_blue(Pm25, Aqi, data_location, Time, Reply_token, formatted_date):
    with open("static/file-etc/pm2.5_blue.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(Aqi, Pm25, data_location, formatted_date, Time)
        #Aqi, Pm25, data_location, formatted_date, Time
    message = FlexSendMessage(alt_text="pm2.5_green", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณภาพอากาศตอนนี้ดีมากครับ")]
    line_bot_api.reply_message(Reply_token, messages)  

def pm_yellow(Pm25, Aqi, data_location, Time, Reply_token, formatted_date):
    with open("static/file-etc/pm2.5_yellow.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(Aqi, Pm25, data_location, formatted_date, Time)
        #Aqi, Pm25, data_location, formatted_date, Time
    message = FlexSendMessage(alt_text="pm2.5_green", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณภาพอากาศตอนนี้ปานกลางครับ")]
    line_bot_api.reply_message(Reply_token, messages)

def pm_orange(Pm25, Aqi, data_location, Time, Reply_token, formatted_date):
    with open("static/file-etc/pm2.5_orange.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(Aqi, Pm25, data_location, formatted_date, Time)
        #Aqi, Pm25, data_location, formatted_date, Time
    message = FlexSendMessage(alt_text="pm2.5_green", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณภาพอากาศตอนนี้เริ่มมีผลกระทบต่อสุขภาพแล้วครับ")]
    line_bot_api.reply_message(Reply_token, messages)

def pm_red(Pm25, Aqi, data_location, Time, Reply_token, formatted_date):
    with open("static/file-etc/pm2.5_red.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(Aqi, Pm25, data_location, formatted_date, Time)
        #Aqi, Pm25, data_location, formatted_date, Time
    message = FlexSendMessage(alt_text="pm2.5_green", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณภาพอากาศตอนนี้มีผลกระทบต่อสุขภาพแล้วครับ")]
    line_bot_api.reply_message(Reply_token, messages)    

def ReplyMessage(Reply_token, TextMessage, Line_Acees_Token, message_type):
    #LINE_API = 'https://api.line.me/v2/bot/message/reply'

    Authorization = 'Bearer {}'.format(Line_Acees_Token)  # ที่ยาวๆ
    # print(Authorization)

    if (message_type == 'text'):
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': Authorization
        }
        data = {
            "replyToken": Reply_token,
            "messages": [
                {
                    "type": "text",
                    "text": TextMessage
                }]
        }
        data = json.dumps(data, ensure_ascii=False)
        requests.post(LINE_API, headers=headers, data=data.encode("utf-8"))

    elif (message_type == 'location'):
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': Authorization
        }
        data = {
            "replyToken": Reply_token,
            "messages": [
                {
                    "type": "text",
                    "text": TextMessage
                }]
        }
        data = json.dumps(data, ensure_ascii=False)
        r = requests.post(LINE_API, headers=headers, data=data.encode("utf-8"))
        print(data)
        print(r)



    return 200


stemmer = LancasterStemmer()
with open("static/file-etc/intents.json", encoding="utf-8") as file:
    data = json.load(file)

with open("static/file-etc/data.pickle", "rb") as f:
    words, labels, training, output = pickle.load(f)
words = []
labels = []
# คำ
docs_x = []
# tag ข้อความ
docs_y = []
for intent in data["intents"]:
    for pattern in intent["patterns"]:
        #wrds = nltk.word_tokenize(pattern)
        #newmm
        #words_tokenize = deepcut.tokenize(pattern)
        words_tokenize = word_tokenize(pattern, engine='newmm',keep_whitespace=False)
        stopwords = list(thai_stopwords())
        s_word_lower = [i for i in words_tokenize if i not in stopwords]
        #words.extend(words_tokenize)
        words.extend(s_word_lower)
        # คำ
        #docs_x.append(words_tokenize)
        docs_x.append(s_word_lower)
        # tag
        docs_y.append(intent["tag"])

    if intent["tag"] not in labels:
        labels.append(intent["tag"])
print("docs_x", docs_x)
print(len(docs_x))  
print("docs_y", docs_y)
print(len(docs_y))
#print ("%s sentences of training data" % len(training_data))
# print(training_data)
print("labels1")
print(labels)  # มันคือ tag
ignore = ["?","!","ๆ"]
#words = [stemmer.stem(w.lower()) for w in words if w != "?"]   
words = [stemmer.stem(w.lower()) for w in words if w not in ignore] 
words = sorted(list(set(words)))  # คำต่างๆ
labels = sorted(labels)
print("words sorted ==",words )

print("labels sorted==",labels )
training = []
output = []
# สร้างอาร์เรย์ 0 เท่ากับจำนวน tag
out_empty = [0 for _ in range(len(labels))]
# enumerate จะได้ค่า index,value
for x, doc in enumerate(docs_x):
    bag = []
    wrds = [stemmer.stem(w.lower()) for w in doc]
    for w in words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)
    # [:] สร้างสำเนาของลำดับดั้งเดิม        
    output_row = out_empty[:]
    # ทำการ แทน เลข 1 ใน output_row ในตำแหน่งที่ตรงกับ labels(มันคือ tag แต่ละประเภท) 
    output_row[labels.index(docs_y[x])] = 1
    training.append(bag)
    output.append(output_row)
    print("bagggg",bag)
with open("static/file-etc/data.pickle", "wb") as f:
    pickle.dump((words, labels, training, output), f)
training = numpy.array(training)
output = numpy.array(output)
print(len(training[0]))
print(len(output[0]))
print("training")
print(training)
print("output")
print(output)
ops.reset_default_graph()

# Build neural network
# inputs
net = tflearn.input_data(shape=[None, len(training[0])])

#Hidden Layer
# weight_decay=0.001
net = tflearn.fully_connected(net, 8, weight_decay=0.001)
net = tflearn.fully_connected(net, 8, weight_decay=0.001)
# dropout ลด Overfit ใช้แค่โมเดลเดียว มาจำลองเป็นหลาย ๆ โมเดลได้ โดยการสุ่มถอดบาง Node ออก ในระหว่างการเทรน
#net = tflearn.dropout(net, 0.5)
# output layer
# learning_rate=0.001,ใช้ regression
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net, optimizer='Adam', learning_rate=0.001, loss='categorical_crossentropy')
model = tflearn.DNN(net)


#train model, save and load model
model.fit(training, output, n_epoch=500, batch_size=8, show_metric=True)
model.save("static/file-etc/model.tflearn")
model.load("static/file-etc/model.tflearn")
# Training Step มาจาก จำนวนข้อมูลทั้งหมด/batch_size
# n_epoch จำนวนรอบในการ train

train_score = model.evaluate(training, output)
print("Training score: {:.2f}".format(train_score[0]))

# s คือ inp , words คือ คำของ model
def bag_of_word(s, words):
    word_bag = [0 for _ in range(len(words))]
    print("len(words)", len(words))
    # print(bag)
    #s_word_tokenize = deepcut.tokenize(s)
    s_word_tokenize = word_tokenize(s,engine='newmm',keep_whitespace=False)
    #new
    stopwords = list(thai_stopwords())
    s_word_lower = [i for i in s_word_tokenize if i not in stopwords]
    #new
    print("s_words")
    #print(s_word_tokenize)
    ignore_words = ["?","!"]
    #s_word_lower = [stemmer.stem(word.lower()) for word in s_word_tokenize if word not in ignore_words]
    s_word_lower = [stemmer.stem(word.lower()) for word in s_word_lower if word not in ignore_words]
    print(s_word_lower)
    #stopwords = list(thai_stopwords())
    #s_word_lower = [i for i in s_word_tokenize if i not in stopwords]
    for se in s_word_lower:
        # enumerate เป็นคำสั่งสำหรับแจกแจงค่า index
        #จะได้ (Index,Value)
        for i, w in enumerate(words):
            if w == se:
                word_bag[i] = (1)
                print(i,w,se)
                #print(se)
    # ตรงนี้เทียบเอาถ้าตรงกับ bag แล้วใส่ 1
    print("bag")
    print(len(numpy.array(word_bag)))
    print("sdsds", numpy.array(word_bag))
    print(numpy.argmax(word_bag))
    return numpy.array(word_bag)


if __name__ == '__main__':
    #app.run(port=200, host="0.0.0.0", debug=True)
    app.run(port=200, debug=True, host="0.0.0.0")