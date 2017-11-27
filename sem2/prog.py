import paho.mqtt.client as mqtt
import time

# The callback for when the client receives a CONNACK response from the server.

colors = {"blue" : ["set 5 1", "set 5 0"], "red" : ["set 6 1", "set 6 0"], "green" : ["set 7 1", "set 7 0"]}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and

    # reconnect then subscriptions will be renewed.

    client.subscribe("devices/lora/#")
    cho = str(input())
    if cho not in colors.keys():
        print("Input not recognized\nTry red, green, blue\n")
    for color in colors.keys():
        if cho == color:
            info = client.publish("devices/lora/807B85902000025D/gpio", colors[color][0])
            print(info)
        else:
            info = client.publish("devices/lora/807B85902000025D/gpio", colors[color][1])
            print(info)




# The callback for when a PUBLISH message is received from the server.

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    pass


client = mqtt.Client()

client.on_connect = on_connect

client.on_message = on_message

client.connect("192.168.4.254")

# Blocking call that processes network traffic, dispatches callbacks and

# handles reconnecting.

# Other loop*() functions are available that give a threaded interface and a

# manual interface.

client.loop_forever()