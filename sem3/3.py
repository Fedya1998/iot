import threading
import time
import json
import queue


def check_input(inp):
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

    if data[item] != "E4000001E70E6401":
        print("Wrong id %d" % data[item])
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
    if data['temperature'] < -20 or data['temperature'] > 100:
        print("Strange temperature %f" % (data['temperature']))
        return False
    if data['temperature'] < 10 or data['temperature'] > 30:
        print("bad temperature %f" % (data['temperature']))
        return False
    if data['humidity'] > 100 or data['humidity'] < 0:
        print("Strange humidity %f" % (data['humidity']))
        return False
    if data['humidity'] > 50 or data['humidity'] < 1:
        print("bad humidity %f" % (data['humidity']))
        return False
    if data['pressure'] < 500 or data['pressure'] > 1500:
        print("Strange pressure %f" % (data['pressure']))
        return False
    if data['pressure'] < 900 or data['pressure'] > 1100:
        print("bad pressure %f" % (data['pressure']))
        return False

    # print("Ok\n")
    return True


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


def check_(queue1):
    time_last = time.time()
    while (1):
        if (queue1.empty()):
            if time.time() - time_last > 30:
                print("red\n")
        else:
            queue1.get()
            time_last = time.time()
            print("green\n")


queue1 = queue.Queue()
t1 = threading.Thread(target=main_, args=(queue1,))
t2 = threading.Thread(target=check_, args=(queue1,))
t1.daemon = True
t1.start()
t2.start()