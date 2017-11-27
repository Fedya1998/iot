import paho.mqtt.client as mqtt
import time
import json
import threading
import time

key = ""

def check_input(inp):
    global key
    super_list = ['\"data\"', '\"id\"', '\"status\"', '\"devEUI\"', '\"rssi\"',
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
    good_keys1 = sorted(['id'])
    good_keys2 = sorted(['devEUI', 'temperature', 'rssi', 'battery', 'date'])
    try:
        msg = json.loads(inp)
    except json.decoder.JSONDecodeError as error:
        print("Wrong format on %d pos: %s%s" % (error.pos, inp[error.pos], inp[error.pos + 1:error.pos + 10]))
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
    # if len(sorted(list(msg['status'].keys()))) > len(good_keys2):
    #    print("Bad keys:")
    #    for i in range(len(sorted(list(msg['status'].keys()))) - len(good_keys2)):
    #        print(sorted(list(msg['status'].keys()))[i])
    #    return False

    data = msg['data']
    status = msg['status']

    item = 'id'
    data_type = type(data[item])
    if data_type != str:
        print("Wrong %s type" % item, data, " value", data[item])
        return False

    if key != "":
        if data[item] != key:
            print("Wrong id %s" % data[item])
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
    if status['devEUI'] != "807B85902000025D":
        print("bad id %s" % (status['devEUI']))
        return False

    if key == "":
        print("new key %s" % data['id'])
        key = data['id']

    # print("Ok\n")
    return True


# The callback for when the client receives a CONNACK response from the server.
TOPIC = "devices/lora/807B85902000025D/ibutton"
TOPIC_TO_WRITE = "devices/lora/807B85902000025D/gpio"

colors = {"blue" : ["set 5 1", "set 5 0"], "red" : ["set 6 1", "set 6 0"], "green" : ["set 7 1", "set 7 0"]}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and

    # reconnect then subscriptions will be renewed.

    client.subscribe(TOPIC)





# The callback for when a PUBLISH message is received from the server.

def on_message(client, userdata, msg):
    print(str(msg.payload)[2:-2])
    green = check_input(str(msg.payload)[2:-1])
    if (green):
        print("green\n")
        client.publish(TOPIC_TO_WRITE, colors['green'][0], qos=0)
        client.publish(TOPIC_TO_WRITE, colors['red'][1], qos=0)
        client.publish(TOPIC_TO_WRITE, colors['blue'][1], qos=0)
    else:
        print("not green\n")
        client.publish(TOPIC_TO_WRITE, colors['red'][0], qos=0)
        client.publish(TOPIC_TO_WRITE, colors['green'][1], qos=0)
        client.publish(TOPIC_TO_WRITE, colors['blue'][1], qos=0)

def main_():
    client = mqtt.Client()

    client.on_connect = on_connect

    client.on_message = on_message

    client.connect("192.168.4.254")

    client.loop_forever()

def main2_():
    client = mqtt.Client()
    client.connect("192.168.4.254")
    while 1:
        time.sleep(300)
        print("too late last green\n")
        client.publish(TOPIC_TO_WRITE, colors['red'][1], qos=0)
        client.publish(TOPIC_TO_WRITE, colors['green'][1], qos=0)
        client.publish(TOPIC_TO_WRITE, colors['blue'][0], qos=0)




t1 = threading.Thread(target=main_)
t2 = threading.Thread(target=main2_)
t1.daemon = True
t1.start()
t2.start()
