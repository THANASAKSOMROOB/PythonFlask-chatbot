from email import message
import time
from flask import Flask, request, abort, jsonify, render_template, redirect, send_from_directory 
import requests
import json
import random
from sklearn.metrics import accuracy_score, precision_score, recall_score
import tflearn
import numpy
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

import sys
import pyodbc as odbc

import uuid


import urllib.parse
import googlemaps

import requests


""" from Project.imageclass.city2 import classified """



# data base config
DRIVER = 'SQL Server'
SERVER_NAME = 'xxxxxxxxxxxxxxx'
DATABASE_NAME = 'xxxxxxxxxxxxxxx'
username = 'xxxxxxxxxxxxxxx' 
password = 'xxxxxxxxxxxxxxx' 

conn_string = f"""
    Driver={{{DRIVER}}};
    Server={SERVER_NAME};
    Database={DATABASE_NAME};
    username={username};
    password={password};
    Trust_Connection=yes;
"""

# ที่อยู่รูปที่บันทึก
dir_path = 'xxxxxxxxxxxxxxx'

# ข้อมูล Line developers chatbot
Channel_access_token = 'xxxxxxxxxxxxxxx'
Channel_secret = 'xxxxxxxxxxxxxxx'
basic_id = 'xxxxxxxxxxxxxxx'
LINE_API = 'https://api.line.me/v2/bot/message/reply'
line_bot_api = LineBotApi(Channel_access_token)

api_key = 'xxxxxxxxxxxxxxx'

# run Flask
app = Flask(__name__)
print("name",   app)




# webhook ส่งข้อมูลกับ Line
global list_data
list_data = []
#global isbool
isbool = True
global list_image
list_image = []

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    global Problem_type
    if request.method == 'POST':
        dataload = request.json
        print(dataload)
        Reply_token = dataload['events'][0]['replyToken']
        message_type = dataload['events'][0]['message']['type']
        if message_type == 'text':
            message = dataload['events'][0]['message']['text']
            userID = dataload['events'][0]['source']['userId']
            global isbool
            global list_data
            inp = message
            results = model.predict([bag_of_word(inp, words)])
            results_index = numpy.argmax(results)
            value_predict = results[0][results_index]
            print(results[0])
            print("re", results)
            print("max", results_index)
            print("max value", results[0][results_index])
            print(labels)
            if (float(value_predict) < 0.75):
                TextMessage = "ผมไม่เข้าใจกรุณาส่งข้อความอีกครั้งครับ"
                records_pre = [[float(value_predict), message]]
                try:
                    conn = odbc.connect(conn_string)
                except Exception as e:
                    print('จบการทำงาน connect error' + e)
                    sys.exit()
                else: 
                    cursor = conn.cursor()
                insert_statement = """ INSERT INTO Data_predict_low VALUES (?, ?) """

                try:
                    for record in records_pre:
                        print(record)
                        cursor.execute(insert_statement, record)        
                except Exception as e:
                    cursor.rollback()
                    print(e)
                    print('บันทึกไม่สำเร็จ')
                else:
                    print('บันทึกเรียบร้อยแล้ว')
                    cursor.commit()
                    cursor.close()
                finally:
                    if conn == 1:
                        print('connection ไม่ได้')
                        conn.close()
                sendtextunderstand(Reply_token, TextMessage)  
            else:
                #เตรียมข้อมูลไปเปิด ticket
                if len(list_data) == 0:
                    list_data.append({'UserID': userID, 'Image':'', 'message':message, 'message1': '', 'message2':''})
                #กรณี list_data ไม่ว่าง
                else:
                    for i in range(len(list_data)):
                        #กรณีมี userID ใน list_data 
                        if  (userID in list_data[i].values()) and (((list_data[i]['message']) != '')) and (((list_data[i]['message1']) == '')):
                            #isbool = False
                            list_data[i].update({'message1':message})  
                        elif ((userID in list_data[i].values()) and (((list_data[i]['message']) != ''))  and (((list_data[i]['message1']) != ''))):
                            list_data[i].update({'message2':message}) 
                        #กรณีไม่มี userID ใน list_data 
                        else:
                            isFound = False
                            for item in list_data:
                                if (userID == item["UserID"]):
                                    isFound = True
                                    break
                           
                            if not isFound:
                                list_data.append({'UserID': userID, 'Image':'', 'message':message, 'message1':'', 'message2':''})
                print("list_data2222222222222222222222", list_data)     
         
                tag = labels[results_index]
                for tg in data["intents"]:
                    if tg['tag'] == tag:
                        responses = tg['responses']
                        re_m = random.choices(responses)
                        Reply_message = ' '.join([str(elem) for elem in re_m])
                        print("คำตอบ", Reply_message)
                        print("tag", tg['tag'])
                        print("ค่า", value_predict)
                        print("text", message)
                        #บันทึกค่า predict
                        tag_data = tg['tag']        
                        records_pre = [[float(value_predict),  tag_data, message]]
                        try:
                            conn = odbc.connect(conn_string)
                        except Exception as e:
                            print('จบการทำงาน connect error' + e)
                            sys.exit()
                        else: 
                            cursor = conn.cursor()
                        insert_statement = """ INSERT INTO Data_predict VALUES (?, ?, ?) """

                        try:
                            for record in records_pre:
                                print(record)
                                cursor.execute(insert_statement, record)        
                        except Exception as e:
                            cursor.rollback()
                            print(e)
                            print('บันทึกไม่สำเร็จ')
                        else:
                            print('บันทึกเรียบร้อยแล้ว')
                            cursor.commit()
                            cursor.close()
                        finally:
                            if conn == 1:
                                print('connection ไม่ได้')
                                conn.close()
                        date = datetime.datetime.now()
                        if tg['tag'] == "greeting":
                            print(tg['tag'])
                            greeting(Reply_token, Reply_message)
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
                        elif tg['tag'] == "rescue_service":
                            state_tag = "rescue_service"
                            data_tag = {
                                        "data_tag":{
                                                "State_tag":"{}".format(state_tag),
                                                "date":"{}".format(date.strftime("%m/%d/%Y")),
                                                "Time":"{}".format(date.strftime("%H:%M:%S"))}}
                            with open('static/file-etc/state_tag.json', 'w') as f:
                                json.dump(data_tag, f)
                            print(state_tag)
                            rescue(Reply_token, Reply_message)
                        elif tg['tag'] == "air_conditioner_information":
                            state_tag = "air_conditioner_information"
                            data_tag = {
                                        "data_tag":{
                                                "State_tag":"{}".format(state_tag),
                                                "date":"{}".format(date.strftime("%m/%d/%Y")),
                                                "Time":"{}".format(date.strftime("%H:%M:%S"))}}
                            with open('static/file-etc/state_tag.json', 'w') as f:
                                json.dump(data_tag, f)
                            print(state_tag)
                            air_condittion(Reply_token, Reply_message)
                        
        elif message_type == 'location':
            userID = dataload['events'][0]['source']['userId']
            data_location = dataload['events'][0]['message']['address']
            lat_ = dataload['events'][0]['message']['latitude']
            long_ = dataload['events'][0]['message']['longitude']
            print(userID)
            print(data_location)
            print(lat_)
            print(long_)
            with open("static/file-etc/state_tag.json", encoding="utf-8") as file:
                data_state_tag = json.load(file)   
                 
                for dst in data_state_tag.values():
                    state_tag = dst['State_tag']
                if (state_tag == "PM2.5"):
                    # api air4thai
                    air4thai_API = requests.get(
                        'http://air4thai.pcd.go.th/services/getNewAQI_JSON.php?')
                    data_api = air4thai_API.text
                    lat = '{}'.format(lat_)
                    long = '{}'.format(long_)
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
                    data_tag = {
                                    "data_tag":{
                                            "State_tag":"{}".format(""),
                                            "date":"{}".format(""),
                                            "Time":"{}".format("")}}
                    with open('static/file-etc/state_tag.json', 'w') as f:
                        json.dump(data_tag, f)            
                elif (state_tag == "no_picture"):
                    data_tag = {
                                    "data_tag":{
                                            "State_tag":"{}".format(""),
                                            "date":"{}".format(""),
                                            "Time":"{}".format("")}}
                    with open('static/file-etc/state_tag.json', 'w') as f:
                        json.dump(data_tag, f)
                    for i in range(len(list_data)):
                        if (userID in list_data[i].values()):
                            Image1 = list_data[i]['Image']
                            message1 = list_data[i]['message1']
                            message = list_data[i]['message']
                    print("list_data3333333333333333333",list_data)        
                    Subject = message
                    Description = message1
                    Location = (data_location + " " + "lat" + " " + '{}'.format(lat_)+ " " + "long" + " "+ '{}'.format(long_))
                    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    data_openticket = {
                                "Subject":'{}'.format(Subject),
                                "Description":'{}'.format(Description),
                                "Location":'{}'.format(Location),
                                "Requester":{"UserID":'{}'.format(userID)}
                    }
                    Message_ = requests.post('xxxxxxxxxxxxxxxxxxxxxxxxxx', data=json.dumps(data_openticket),headers=headers)
                    mes_ = (Message_.text).split('"')[1]
                    
                    Reply_message = 'ขอบคุณสำหรับปัญหาที่แจ้งมาครับ'
                    res = [i for i in list_data if not (i['UserID'] == userID)]
                    list_data.clear()  
                    for i in res:
                        list_data.append(i) 
                    print("ลบแล้ววววว",list_data)
                    if len(mes_) > 0:
                        ticket_id(Reply_token, mes_, Reply_message)
                    else:
                        TextMessage = "แจ้งปัญญาไม่สำเร็จกรุณาติดต่อเจ้าหน้าที่"
                        caseerror(Reply_token, TextMessage) 
                elif (state_tag == "rescue_service"):
                    data_tag = {
                                    "data_tag":{
                                            "State_tag":"{}".format(""),
                                            "date":"{}".format(""),
                                            "Time":"{}".format("")}}
                    with open('static/file-etc/state_tag.json', 'w') as f:
                        json.dump(data_tag, f)

                    lat = '{}'.format(dataload['events'][0]['message']['latitude'])
                    long = '{}'.format(dataload['events'][0]['message']['longitude'])    
                    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={}%2C{}&radius=15000&type=กู้ภัย|มูลนิธิ&keyword=กู้ภัยมูลนิธิ&key={}".format(lat,long,api_key)
                    payload={}
                    headers = {}
                    response = requests.request("GET", url, headers=headers, data=payload)
                    data_rescue = response.json()
                    place_res = []
                    for place in data_rescue['results']:
                        place_res.append(place['name'])
                    place01 = place_res[0]
                    place_res11 = place_res[0]
                    place_res02 = place_res[1]
                    place_res22 = place_res[1]
                    place_res03 = place_res[2] 
                    place_res33 = place_res[2]
                    place_res04 = place_res[5]
                    place_res44 = place_res[5] 
                    place_res05 = place_res[4]   
                    place_res55 = place_res[4]
                    origin_addresses = dataload['events'][0]['message']['address']
                    bubble_rescue(origin_addresses,Reply_token, place01, place_res11, place_res02, place_res22, place_res03, place_res33, place_res04, place_res44, place_res05, place_res55)    
                elif (state_tag == "air_conditioner_information"):
                    data_tag = {
                                    "data_tag":{
                                            "State_tag":"{}".format(""),
                                            "date":"{}".format(""),
                                            "Time":"{}".format("")}}
                    with open('static/file-etc/state_tag.json', 'w') as f:
                        json.dump(data_tag, f)
                    lat = '{}'.format(dataload['events'][0]['message']['latitude'])
                    long = '{}'.format(dataload['events'][0]['message']['longitude'])    
                    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={}%2C{}&radius=15000&type==ร้ายขายแอร์|เครื่องปรับอากาศ&keyword=ร้านขายเครื่องปรับอากาศ&key={}".format(lat,long,api_key)
                    payload={}
                    headers = {}
                    response = requests.request("GET", url, headers=headers, data=payload)
                    data_air = response.json()
                    air_res = []
                    for air in data_air['results']:
                        air_res.append(air['name'])
                    air_res01 = air_res[0]
                    air_res11 = air_res[0]
                    air_res02 = air_res[1]
                    air_res22 = air_res[1]
                    air_res03 = air_res[2] 
                    air_res33 = air_res[2]
                    air_res04 = air_res[3]
                    air_res44 = air_res[3] 
                    air_res05 = air_res[4]   
                    air_res55 = air_res[4]
                    origin_addresses = dataload['events'][0]['message']['address']
                    air_conditioner_info(origin_addresses, Reply_token, air_res01, air_res11, air_res02, air_res22, air_res03, air_res33, air_res04, air_res44, air_res05, air_res55)                     
                    
                else:
                    print(state_tag)
                    message_type = dataload['events'][0]['message']['type']
                    Reply_message = 'ขอบคุณสำหรับปัญหาที่แจ้งมาครับ'
                    for i in range(len(list_data)):
                        if (userID in list_data[i].values()):
                            Image1 = list_data[i]['Image']
                            message1 = list_data[i]['message1']
                            message2 = list_data[i]['message2']
                            message = list_data[i]['message']

                    print("list ก่อนส่ง33333333333333333333333333", list_data)
                    Subject = message
                    Description = message1
                    Location = (data_location + " " + "lat" + " " + '{}'.format(lat_)+ " " + "long" + " "+ '{}'.format(long_))
                    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    data_openticket = {
                                "Subject":'{}'.format(Subject),
                                "Description":'{}'.format(Description),
                                "Location":'{}'.format(Location),
                                "Requester":{"UserID":'{}'.format(userID)}
                    }
                    Message_ = requests.post('xxxxxxxxxxxxxxxxxxxxxxxxxx', data=json.dumps(data_openticket),headers=headers)
                    mes_ = (Message_.text).split('"')[1]
                    print("data_openticket",data_openticket)
                    
                    res = [i for i in list_data if not (i['UserID'] == userID)]
                    list_data.clear()  
                    for i in res:
                        list_data.append(i)
                    print("ลบแล้ววววว",list_data)

                    if len(mes_) > 0:
                        ticket_id(Reply_token, mes_, Reply_message)
                    else:
                        TextMessage = "แจ้งปัญญาไม่สำเร็จกรุณาติดต่อเจ้าหน้าที่"
                        caseerror(Reply_token, TextMessage)                                          

        elif message_type == 'image':
            if 'imageSet' in dataload['events'][0]['message']:
                isone = False
                total_img = dataload['events'][0]['message']['imageSet']['total']
                Count_image = dataload['events'][0]['message']['imageSet']['total']
                Userid = dataload['events'][0]['source']['userId']
                imageid = dataload['events'][0]['message']['imageSet']['id']
                date = datetime.datetime.now()
                print("total_img",total_img)
                print("Count_image",Count_image)
                print("Userid",Userid)
                print("imageid",imageid)
                
                
            else:
                total_img = 1
                isone = True
                Count_image = "1"
                Userid = dataload['events'][0]['source']['userId']
                date = datetime.datetime.now()
            for x in dataload['events']:
                message_id = x['message']['id']
                list_image.append(message_id)
                message_contents = line_bot_api.get_message_content(message_id)
                with open('static/file-etc/file_path', 'wb') as fd:
                    for chunk in message_contents.iter_content(chunk_size=720*720):
                        fd.write(chunk)
                with open('static/file-etc/file_path', mode='rb') as file:
                    filepath = file.read()
                    img = Image.open(io.BytesIO(filepath))

                filename = 'pic{}.jpg'.format(message_id)
                file_path_save = os.path.join(dir_path, filename)
                img.save(file_path_save)

        
                records = [[Userid, Count_image, filename, imageid, date]]
                try:
                    conn = odbc.connect(conn_string)
                except Exception as e:
                    print('จบการทำงาน connect error' + e)
                    sys.exit()
                else: 
                    cursor = conn.cursor()
                insert_statement = """ INSERT INTO Data_image VALUES (?, ?, ?, ?, ?) """
                try:
                    for record in records:
                        print(record)
                        cursor.execute(insert_statement, record)        
                except Exception as e:
                    cursor.rollback()
                    print(e)
                    print('บันทึกไม่สำเร็จ')
                else:
                    print('บันทึกเรียบร้อยแล้ว')
                    cursor.commit()
                    cursor.close()
                finally:
                    if conn == 1:
                        print('connection ไม่ได้')
                        conn.close()

            print("listimg", list_image)
            userID = dataload['events'][0]['source']['userId']
            lst = ''
            for img in range(len(list_image)):
                lst += list_image[img]+'/'

            for i in range(len(list_data)):
                    #กรณีมี userID ใน list_data 
                    if (userID in list_data[i].values()):
                        list_data[i].update({'Image':lst})     
            print(list_data)
            # มีไวเพื่อล้างข้อมูลในไฟล์ file_path
            with open('static/file-etc/file_path', 'wb') as fd:
                fd.close()

            # location action
            # SELECT Count
            try:
                conn = odbc.connect(conn_string)
            except Exception as e:
                print('จบการทำงาน connect error' + e)
                sys.exit()
            else:
                cursor = conn.cursor()

            insert_statement = """SELECT Count(Image_id)as Count_image_id FROM Data_image WHERE Image_id = '{}'""".format(imageid)
            cursor.execute(insert_statement)
            myresult = cursor.fetchone() 
            my_result = list(myresult)
            print("my_result", my_result)
            
            imageclassification_API = requests.get('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'.format(imageid))
            Message_API = imageclassification_API.text
            Text_Message = ""
            if str(Message_API) == "potholes":
                Text_Message = "ถนนเป็นหลุมเป็นบ่อ"
            elif str(Message_API) == "flood":
                Text_Message = "น้ำท่วม"   
            elif str(Message_API) == "trash":
                Text_Message = "ขยะ"
            if (int(my_result[0]) == int(total_img)) or ((int(total_img)==1) and isone):
                Quick_Reply(Reply_token)
                conn.close() 

        return request.json, 200
    elif request.method == 'GET':

        return 'this is method GET!! เอาไว้ส่งข้อมูลไปมากับไลน์', 200
    else:
        abort(400)


@app.route('/')
def Hello():
    return 'Hello', 200

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/chatbot.jpg')    

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


@app.route('/api/chatbot', methods=['POST','GET'])
def chatbot_api():
    if request.method == 'GET':
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

def test(Reply_token, TextMessage):
    line_bot_api.reply_message(
        Reply_token,
        TextSendMessage(text=TextMessage))        

def rescue(Reply_token, TextMessage):
    message = TextSendMessage(
            text=TextMessage,
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=LocationAction(label="Send location")
                    ),
                ]))
    messages = [message]
    line_bot_api.reply_message(Reply_token, messages)   

def air_condittion(Reply_token, TextMessage):
    message = TextSendMessage(
            text=TextMessage,
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=LocationAction(label="Send location")
                    ),
                ]))
    messages = [message]
    line_bot_api.reply_message(Reply_token, messages)         

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
    with open("static/file-etc/ticketid.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(TextMessage)
    message = FlexSendMessage(
        alt_text="problem", contents=json.loads(bbs))
    messages = [    
        message,
        TextSendMessage(text=Reply_message)
    ]   
    line_bot_api.reply_message(Reply_token, messages)
    

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



def test1150(Reply_token):
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
    message = FlexSendMessage(alt_text="pm2.5_green", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณภาพอากาศตอนนี้ดีครับ")]
    line_bot_api.reply_message(Reply_token, messages)

def pm_blue(Pm25, Aqi, data_location, Time, Reply_token, formatted_date):
    with open("static/file-etc/pm2.5_blue.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(Aqi, Pm25, data_location, formatted_date, Time)
    message = FlexSendMessage(alt_text="pm2.5_green", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณภาพอากาศตอนนี้ดีมากครับ")]
    line_bot_api.reply_message(Reply_token, messages)  

def pm_yellow(Pm25, Aqi, data_location, Time, Reply_token, formatted_date):
    with open("static/file-etc/pm2.5_yellow.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(Aqi, Pm25, data_location, formatted_date, Time)

    message = FlexSendMessage(alt_text="pm2.5_green", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณภาพอากาศตอนนี้ปานกลางครับ")]
    line_bot_api.reply_message(Reply_token, messages)

def pm_orange(Pm25, Aqi, data_location, Time, Reply_token, formatted_date):
    with open("static/file-etc/pm2.5_orange.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(Aqi, Pm25, data_location, formatted_date, Time)
    message = FlexSendMessage(alt_text="pm2.5_green", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณภาพอากาศตอนนี้เริ่มมีผลกระทบต่อสุขภาพแล้วครับ")]
    line_bot_api.reply_message(Reply_token, messages)

def pm_red(Pm25, Aqi, data_location, Time, Reply_token, formatted_date):
    with open("static/file-etc/pm2.5_red.json", encoding="utf-8") as file:
        data = json.load(file)
        bubble_string = '{}'.format(data)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(Aqi, Pm25, data_location, formatted_date, Time)
    message = FlexSendMessage(alt_text="pm2.5_green", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณภาพอากาศตอนนี้มีผลกระทบต่อสุขภาพแล้วครับ")]
    line_bot_api.reply_message(Reply_token, messages)  



def bubble_rescue(origin_addresses,Reply_token, place_res01, place_res11, place_res02, place_res22, place_res03, place_res33, place_res04, place_res44, place_res05, place_res55):
    maps = googlemaps.Client(key=api_key)
    data_place_res11 = maps.distance_matrix(origin_addresses, place_res11)
    print("data_place_res11", data_place_res11)
    data_place_res22 = maps.distance_matrix(origin_addresses, place_res22)
    print("data_place_res22", data_place_res22)
    data_place_res33 = maps.distance_matrix(origin_addresses, place_res33)
    data_place_res44 = maps.distance_matrix(origin_addresses, place_res44)
    data_place_res55 = maps.distance_matrix(origin_addresses, place_res55)
    distance_res11 = data_place_res11['rows'][0]['elements'][0]['distance']['text']
    time_res11 = data_place_res11['rows'][0]['elements'][0]['duration']['text']
    distance_res22 = data_place_res22['rows'][0]['elements'][0]['distance']['text']
    time_res22 = data_place_res22['rows'][0]['elements'][0]['duration']['text']
    distance_res33 = data_place_res33['rows'][0]['elements'][0]['distance']['text']
    time_res33 = data_place_res33['rows'][0]['elements'][0]['duration']['text']
    distance_res44 = data_place_res44['rows'][0]['elements'][0]['distance']['text']
    time_res44 = data_place_res44['rows'][0]['elements'][0]['duration']['text']
    distance_res55 = data_place_res55['rows'][0]['elements'][0]['distance']['text']
    time_res55 = data_place_res55['rows'][0]['elements'][0]['duration']['text']
    place_res01 = 'https://www.google.com/maps/search/'+urllib.parse.quote_plus(place_res01)
    place_res02 = 'https://www.google.com/maps/search/'+urllib.parse.quote_plus(place_res02)
    place_res03 = 'https://www.google.com/maps/search/'+urllib.parse.quote_plus(place_res03)
    place_res04 = 'https://www.google.com/maps/search/'+urllib.parse.quote_plus(place_res04)
    place_res05 = 'https://www.google.com/maps/search/'+urllib.parse.quote_plus(place_res05)
    with open("static/file-etc/rescue_service.json", encoding="utf-8") as file:
        data_rescue = json.load(file)  
        bubble_string = '{}'.format(data_rescue)
        bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(place_res11, distance_res11, time_res11, place_res01, place_res22, distance_res22, time_res22, place_res02, place_res33, distance_res33, time_res33, place_res03, place_res44, distance_res44, time_res44, place_res04, place_res55, distance_res55, time_res55, place_res05)
    message = FlexSendMessage(alt_text="rescue", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณสามารถเลือกหน่วยกู้ภัยที่อยู่ใกล้ที่สุด")]
    line_bot_api.reply_message(Reply_token, messages)  

def air_conditioner_info(origin_addresses, Reply_token, air_res01, air_res11, air_res02, air_res22, air_res03, air_res33, air_res04, air_res44, air_res05, air_res55):
    maps = googlemaps.Client(key=api_key)
    data_air_res11 = maps.distance_matrix(origin_addresses, air_res11)
    data_air_res22 = maps.distance_matrix(origin_addresses, air_res22)
    data_air_res33 = maps.distance_matrix(origin_addresses, air_res33)
    data_air_res44 = maps.distance_matrix(origin_addresses, air_res44)
    data_air_res55 = maps.distance_matrix(origin_addresses, air_res55)
    distance_res11 = data_air_res11['rows'][0]['elements'][0]['distance']['text']
    time_res11 = data_air_res11['rows'][0]['elements'][0]['duration']['text']
    distance_res22 = data_air_res22['rows'][0]['elements'][0]['distance']['text']
    time_res22 = data_air_res22['rows'][0]['elements'][0]['duration']['text']
    distance_res33 = data_air_res33['rows'][0]['elements'][0]['distance']['text']
    time_res33 = data_air_res33['rows'][0]['elements'][0]['duration']['text']
    distance_res44 = data_air_res44['rows'][0]['elements'][0]['distance']['text']
    time_res44 = data_air_res44['rows'][0]['elements'][0]['duration']['text']
    distance_res55 = data_air_res55['rows'][0]['elements'][0]['distance']['text']
    time_res55 = data_air_res55['rows'][0]['elements'][0]['duration']['text']
    air_res01 = 'https://www.google.com/maps/search/'+urllib.parse.quote_plus(air_res01)
    air_res02 = 'https://www.google.com/maps/search/'+urllib.parse.quote_plus(air_res02)
    air_res03 = 'https://www.google.com/maps/search/'+urllib.parse.quote_plus(air_res03)
    air_res04 = 'https://www.google.com/maps/search/'+urllib.parse.quote_plus(air_res04)
    air_res05 = 'https://www.google.com/maps/search/'+urllib.parse.quote_plus(air_res05)
    with open("static/file-etc/air.json", encoding="utf-8") as file:
        data_air = json.load(file)  
        bubble_string = '{}'.format(data_air)
    bbs = bubble_string.replace("\'", "\"").replace("True", "true")%(air_res11, distance_res11, time_res11, air_res01, air_res22, distance_res22, time_res22, air_res02, air_res33, distance_res33, time_res33, air_res03, air_res44, distance_res44, time_res44, air_res04, air_res55, distance_res55, time_res55, air_res05)
    message = FlexSendMessage(alt_text="air", contents=json.loads(bbs))
    messages = [message,TextSendMessage(text="คุณสามารถเลือกร้านเครื่องปรับอากาศที่อยู่ใกล้ที่สุด")]
    line_bot_api.reply_message(Reply_token, messages)

def ReplyMessage(Reply_token, TextMessage, Line_Acees_Token, message_type):

    Authorization = 'Bearer {}'.format(Line_Acees_Token)  

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
        words_tokenize = word_tokenize(pattern, engine='newmm',keep_whitespace=False)
        stopwords = list(thai_stopwords())
        s_word_lower = [i for i in words_tokenize if i not in stopwords]
        words.extend(s_word_lower)
        docs_x.append(s_word_lower)
        docs_y.append(intent["tag"])

    if intent["tag"] not in labels:
        labels.append(intent["tag"])
print("docs_x", docs_x)
print(len(docs_x))  
print("docs_y", docs_y)
print(len(docs_y))
print("labels1")
print(labels)  
ignore = ["?","!","ๆ"]
words = [stemmer.stem(w.lower()) for w in words if w not in ignore] 
words = sorted(list(set(words)))  
labels = sorted(labels)
print("words sorted ==",words )

print("labels sorted==",labels )
training = []
output = []
out_empty = [0 for _ in range(len(labels))]
for x, doc in enumerate(docs_x):
    bag = []
    wrds = [stemmer.stem(w.lower()) for w in doc]
    for w in words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)      
    output_row = out_empty[:]
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
print(training.shape)
print("output")
print(output.shape)
print(output)
ops.reset_default_graph()

# Build neural network
# inputs
net = tflearn.input_data(shape=[None, len(training[0])])

#Hidden Layer
# weight_decay=0.001
net = tflearn.fully_connected(net, 8, weight_decay=0.001,  bias_init='zeros')
net = tflearn.fully_connected(net, 8, weight_decay=0.001,  bias_init='zeros')

# output layer
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")

net = tflearn.regression(net, optimizer='Adam', learning_rate=0.001, loss='categorical_crossentropy')
model = tflearn.DNN(net)


#train model, save and load model
try:
    model.load("static/file-etc/model.tflearn")
except:
    model.fit(training, output, n_epoch=500, batch_size=8, show_metric=True)
    model.save("static/file-etc/model.tflearn")



train_score = model.evaluate(training, output)
print("Training score: {:.10f}".format(train_score[0]))
print(train_score)

# s คือ inp , words คือ คำของ model
def bag_of_word(s, words):
    word_bag = [0 for _ in range(len(words))]
    print("len(words)", len(words))
    s_word_tokenize = word_tokenize(s,engine='newmm',keep_whitespace=False)
    stopwords = list(thai_stopwords())
    s_word_lower = [i for i in s_word_tokenize if i not in stopwords]
    print("s_words")
    ignore_words = ["?","!"]
    s_word_lower = [stemmer.stem(word.lower()) for word in s_word_lower if word not in ignore_words]
    print(s_word_lower)

    for se in s_word_lower:
        # enumerate เป็นคำสั่งสำหรับแจกแจงค่า index
        #จะได้ (Index,Value)
        for i, w in enumerate(words):
            if w == se:
                word_bag[i] = (1)
                print(i,w,se)
                
    # ตรงนี้เทียบเอาถ้าตรงกับ bag แล้วใส่ 1
    print("bag")
    print(len(numpy.array(word_bag)))
    print("sdsds", numpy.array(word_bag))
    print(numpy.argmax(word_bag))
    return numpy.array(word_bag)


if __name__ == '__main__':
    app.run(port=200, debug=True, host="0.0.0.0")