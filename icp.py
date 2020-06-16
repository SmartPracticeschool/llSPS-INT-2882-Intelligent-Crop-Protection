import json
from watson_developer_cloud import VisualRecognitionV3
import ibmiotf.application
import ibmiotf.device
import time
import sys
import random
import cv2
import numpy as np
import datetime

organization = "mbtnji"
deviceType = "raspberrypi"
deviceId = "123456"
authMethod = "token"
authToken = "12345678"


def myCommandCallback(cmd):
        #print("Command received: %s" % cmd.data)
        if cmd.data['command']=='motoron':
                print("motor is ON")
        elif cmd.data['command']=='motoroff':
                print("motor is OFF")#Commands
        

try:
	deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
	deviceCli = ibmiotf.device.Client(deviceOptions)


except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()
	
visual_recognition = VisualRecognitionV3(
    '2018-03-19',
    iam_apikey='Ld9hL3NFgXhD8zXydy9mfbbhap6yaEepgqqqytCttOul')
# Connect and send a datapoint "hello" with value "world" into the cloud as an event of type "greeting" 10 times
deviceCli.connect()
# Disconnect the device and application from the cloud
#deviceCli.disconnect()

def vis(ifile):
    with open('./'+ifile, 'rb') as images_file:
        a = visual_recognition.classify(
            images_file,
            threshold='0.6',
            classifier_ids='default').get_result()
        b=a["images"][0]["classifiers"][0]["classes"]
        k=[]
        for i in b:
            k.append(i["class"])
        for j in k:
            if j=="bird":
                a="found"
                break
            elif j=="animal":
                a="found"
                break
            else:
                a="not found"
    return a


video=cv2.VideoCapture(0)

while True:
        #capture the first frame
        check,frame=video.read()
        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('face detection', frame)
        picname=datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
        cv2.imwrite(picname+".jpg",frame)
        f=picname+'.jpg'
        a=vis(f)
        temp = random.randint(0,100)
        hum = random.randint(0,100)
        moist = random.randint(0,100)
        #Send Temperature & Humidity to IBM Watson
        data = { 'Temperature': temp, 'Humidity': hum, 'Moisture': moist, 'data' : a }
        #print (data)
        def myOnPublishCallback():
                print("Published Temperature: %s C " % temp, "Humiidity %s  " % hum, "Moisture %s " % moist, "Recognized data: %s" % a, "to IBM Watson")
        #time.sleep(5)
                
        success = deviceCli.publishEvent("evt1", "json", data, qos=0, on_publish=myOnPublishCallback)

        if not success:
                print("Not connected to IoTF")
                    
        deviceCli.commandCallback = myCommandCallback
        #waitKey(1)- for every 1 millisecond new frame will be captured
        Key=cv2.waitKey(1)
        if Key==ord('q'):
                #release the camera
                video.release()
                #destroy all windows
                cv2.destroyAllWindows()
                break
