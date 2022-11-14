import requests
import random
import time
import datetime
import threading
import uuid
from r305 import R305

ENDPOINT = "things.ubidots.com"
DEVICE_LABEL = "RPI3B"
VARIABLE_LABEL = "keystr"
TOKEN = "A1E-2UDk2wwz6YBfRTuQTR70ZXqqJX9S6a"
string_length = 10
renew_sec = 180
keygen = ""
next_call = time.time()
device = '/dev/ttyUSB0'
baudrate = 57600
dev = R305(device, baudrate)
debug = True#False
authfid = [0,1,2,3,4,5]
fail_ctr = 0
fail_key = ['','','']
max_fail = 3
wait = 0

def my_random_string(string_length):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-","")
    return random[0:string_length]

def get_var(url=ENDPOINT, device=DEVICE_LABEL, variable=VARIABLE_LABEL,token=TOKEN):
    variable = 'fail_list'
    try:
        url = "http://{}/api/v1.6/devices/{}/{}/lv".format(url,device,variable)
        headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
        attempts = 0
        status_code = 400
        while status_code >= 400 and attempts < 5:
            if debug:
                print("[INFO] Retrieving data, attempt number: {}".format(attempts))
            req = requests.get(url=url, headers=headers)
            status_code = req.status_code
            attempts += 1
            time.sleep(1)
            if debug:
                print("[INFO] Results:")
                print(req.text)
    except Exception as e:
        print("[ERROR] Error posting, details: {}".format(e))
    return req.text

def post_var(payload, url=ENDPOINT, device=DEVICE_LABEL, token=TOKEN):
    try:
        url = "http://{}/api/v1.6/devices/{}".format(url, device)
        headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
        attempts = 0
        status_code = 400
        while status_code >= 400 and attempts < 5:
            if debug:
                print("[INFO] Sending data, attempt number: {}".format(attempts))
            req = requests.post(url=url, headers=headers,json=payload)
            status_code = req.status_code
            attempts += 1
            time.sleep(1)
            if debug:
                print("[INFO] Results:" + req.text)
    except Exception as e:
        if debug:
            print("[ERROR] Error posting, details: {}".format(e))

def go():
    global next_call
    global keygen
    global wait
    if debug:
        print("[INFO] Go() called at", datetime.datetime.now())
    next_call = next_call + renew_sec
    threading.Timer( next_call - time.time(), go).start()
    if wait == 0:
        keygen = my_random_string(10)
        if debug:
            print("[INFO] New Key Generated = " + keygen + " at " + time.ctime())
        payload = {VARIABLE_LABEL: {"value":0,"context":{"Key": keygen}}}
        post_var(payload)

def main():
    global keygen
    global dev
    global fail_ctr
    global fail_key
    global wait
    go()
    while True:
        user_ip=raw_input(' Please Enter the Code to Unlock the Locker : ')
        if(user_ip == keygen):
            print(' Put your Finger on the Scanner !!!')
            print(' Waiting for finger')
            while True:
                result = dev.SearchFingerPrint()
                if type(result) == dict:
                    if debug:
                        print('[INFO] Type : ',type(result['matchstore']),' Finger Found at ID = ',result['matchstore'])
                        if result['matchstore'] in authfid :
                            if debug:
                                print('[INFO] thumb LOL')
                            if(user_ip == keygen):
                                print(' ***** Locker is unocked!***** ')
                                fail_ctr = 0
                            else:
                                if debug:
                                    print('Key has been Regnerated!!!')
                                print('Try Again!!')
        else:
            print(' ***** Invalid Code!!!! Locker is Locked *****')
            fail_key[fail_ctr] = user_ip
            fail_ctr+=1
            payloadn = {'fail_list': {"value":0,"context":{"Key": user_ip}}}
            post_var(payloadn)
            if fail_ctr == max_fail:
                if debug:
                    print('Continuous Wrong Attempts Limit Reached,Contact Administrator!!')
                lock = 'Continuous Wrong Attempts Limit Reached!!'
                payloadx = {'fail_list': {"value":1,"context":{"Key": lock}}}
                post_var(payloadx)
                wait = 1
                while True:
                    resultx=get_var()
                    if resultx == '0.0':
                        wait = 0
                        break
                    
if __name__ == "__main__":
    while True:
        main()