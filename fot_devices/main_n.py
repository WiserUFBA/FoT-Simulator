import paho.mqtt.client as mqtt
import json

from time import sleep
from multiprocessing import Process
import argparse
#You don't need to change this file. Just change sensors.py and config.json

parser = argparse.ArgumentParser(description = 'Params sensors')
parser.add_argument('--name', action = 'store', dest = 'name', required = True)
parser.add_argument('--broker', action = 'store', dest = 'broker', required = True)
args = parser.parse_args()

#process list
procs=[]

#create new virtual sensors instances 
class tatu_process(Process):
    def __init__(self,obj,msg,process_id,method_target):
        Process.__init__(self)
        self.obj=obj
        self.msg=msg
        self.process_id=process_id
        self.method_target=method_target
        
    def run(self):
        import tatu_n
        tatu_n.main(self.obj, self.msg)

def on_connect(mqttc, obj, flags, rc):
    topic = obj["topicPrefix"] + obj["deviceName"] + obj["topicReq"] + "/#"
    mqttc.subscribe(topic)
    #print("Device's sensors:")
    #for sensor in obj['sensors']:
    #	print ("\t" + sensor['name'])
    #print("Topic device subscribed: " + topic)

def on_message(mqttc, obj, msg):
    if obj["topicReq"] in msg.topic:
        tatu_msg=json.loads(msg.payload)
        if(tatu_msg['method'].upper()=='STOP'):
            stop_sensor(obj,tatu_msg)
        else:
            init_sensor(obj,tatu_msg,msg)
        

def on_disconnect(mqttc, obj, rc):
	print("disconnected!")
	exit()

def init_sensor(obj,tatu_msg,msg):
    if(tatu_msg.get('sensor')!=None):
        process_id=tatu_msg['method']+'_'+obj['deviceName']+'_'+tatu_msg['sensor']
    else:
        process_id=tatu_msg['method']+'_'+obj['deviceName']
    method_target=tatu_msg['method']
    p = tatu_process(obj,msg,process_id,method_target)
    #print("ID Processo", process_id)
    procs.append(p)
    p.start()

def stop_sensor(obj,tatu_msg):
    for proc in procs:
        if(tatu_msg.get('sensor')!=None):
            process_id=proc.method_target+'_'+obj['deviceName']+'_'+tatu_msg['sensor']
        else:
            process_id=proc.method_target+'_'+obj['deviceName']
        if (proc.process_id==process_id):
            proc.terminate()
            continue
            procs.remove(proc)


while True:
    with open('fot_devices/config.json') as f:
        data = json.load(f)
	
    mqttBroker = args.broker
    mqttPort = data["mqttPort"]
    mqttUsername = data["mqttUsername"]
    mqttPassword = data["mqttPassword"]
    deviceName = args.name
    data["deviceName"]=args.name
    
    #for 2.0 and newer versions of paho-mqtt use that:
    sub_client =mqtt.Client(client_id=deviceName + "_sub", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)
    #see changes in: https://github.com/eclipse/paho.mqtt.python/blob/master/docs/migrations.rst

    #for 1.x versions of paho-mqtt use that: 
    #sub_client = mqtt.Client(deviceName + "_sub", protocol=mqtt.MQTTv31)


    sub_client.username_pw_set(mqttUsername, mqttPassword)
    sub_client.user_data_set(data)
    sub_client.on_connect = on_connect
    sub_client.on_message = on_message
    sub_client.on_disconnect = on_disconnect

    try:
        sub_client.connect(mqttBroker, mqttPort, 60)
        sub_client.loop_forever()
    except:
        print ("Broker unreachable on " + mqttBroker + " URL!")
        sleep(5)
