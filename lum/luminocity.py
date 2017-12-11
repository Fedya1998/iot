import paho.mqtt.client as mqtt
import time
import json
import threading
import time
import math

TOPIC = \
    "devices/6lowpan/02124b000c468202/opt3001"
TOPIC_TO_WRITE = \
    "devices/6lowpan/02124b000c468202/pwm"


def check_input(inp):
    super_list = ['\"data\"', '\"luminocity\"', '\"status\"', '\"devEUI\"', '\"rssi\"',
                  '\"temperature\"', '\"battery\"',
                  '\"date\"']

    pos = 0
    pos2 = len(inp)
    itm = None
    for item in super_list:
        if itm == item:
            pos2 = -1
            itm = None
        pos = inp.find(item, pos)

        if pos == -1:
            print("no such word %s or it was earlier that should be" % (item))
            return False
        pos2__ = inp.find(item, pos + 1)
        if pos2__ != -1:
            pos2 = pos2__
            itm = item
        if pos > pos2 and pos2 != -1:
            print("duplicate word %s, pos %d, pos2 %d" % (itm, pos, pos2))
            return False
            # print(pos, pos2)

    good_keys0 = sorted(['status', 'data'])
    good_keys1 = sorted(['luminocity'])
    good_keys2 = sorted(['devEUI', 'temperature', 'rssi', 'battery', 'date'])
    try:
        msg = json.loads(inp)
    except json.decoder.JSONDecodeError as error:
        print("Wrong format on %d pos--->%s%s" % (
              error.pos, inp[error.pos], inp[error.pos + 1:error.pos + 10]))
        return False
    if type(msg) != dict:
        print("Wrong format, {..} expected")
        return False

    for i in range(len(good_keys0)):
        if sorted(list(msg.keys()))[i] != good_keys0[i]:
            print("Bad key", sorted(list(msg.keys()))[i])
            return False

    for i in range(len(good_keys1)):
        if sorted(list(msg['data'].keys()))[i] != good_keys1[i]:
            print("Bad key", sorted(list(msg['data'].keys()))[i])
            return False

    for i in range(len(good_keys2)):
        if sorted(list(msg['status'].keys()))[i] != good_keys2[i]:
            print("Bad key", sorted(list(msg['status'].keys()))[i])
            return False

    data = msg['data']
    status = msg['status']

    for item in good_keys1:
        data_type = type(data[item])
        if data_type != float and data_type != int:
            print("Wrong %s type" % item, data, " value", data[item])
            return False

    for item in ['rssi', 'temperature', 'battery']:
        data_type = type(status[item])
        if data_type != float and data_type != int:
            print("Wrong %s type" % item, data, " value", status[item])
            return False
    for item in ['devEUI', 'date']:
        data_type = type(status[item])
        if data_type != str:
            print("Wrong %s type" % item, data, " value", status[item])
            return False
    if status['devEUI'] != "02124b000c468202":
        print("bad id %s" % (status['devEUI']))
        return False
    if data['luminocity'] < 0:
        print("Strange luminocity %f" % (data['luminocity']))
        return False
    return data['luminocity']


def main_(queue1):
    global time_last

    while (1):
        try:
            inp = str(input())
            check_input(inp)
            queue1.put(1)
        except KeyError or SyntaxError:
            print("Bad data %s" % (inp))
            pass

#
#def check_(queue1):
#    time_last = time.time()
#    while (1):
#        if (queue1.empty()):
#            if time.time() - time_last > 100:
#                return False
#        else:
#            queue1.get()
#            time_last = time.time()
#
#
#queue1 = queue.Queue()
#t1 = threading.Thread(target=main_, args=(queue1,))
#t2 = threading.Thread(target=check_, args=(queue1,))
#t1.daemon = True
#t1.start()
#t2.start()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(TOPIC)

message_to_send = "set freq 800 dev 01 on ch 01 duty "#lum 0 -> duty 100

def on_message(client, userdata, msg):
    print("get msg %s" %str(msg.payload)[2:-1])
    if (str(msg.payload)[2:-1] != 'send' and str(msg.payload)[2:-1] != 'get'):
        lum = check_input(str(msg.payload)[2:-1])
        if lum != False:
            if lum > 2000:
                duty = 1
            else:
                duty = 100 - lum / 20
            client.publish(TOPIC_TO_WRITE, message_to_send + str(int(duty)),
                           qos=0)
            print("Get lum %d, set duty %d" %(lum, int(duty)))

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.4.254")
client.loop_forever()
