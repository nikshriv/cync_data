import json

Capabilities = {
    "ONOFF":[1,5,6,7,8,9,10,11,13,14,15,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,48,49,51,52,53,54,55,56,57,58,59,61,62,63,64,65,66,67,68,80,81,82,83,85,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,156,158,159,160,161,162,163,164,165],
    "BRIGHTNESS":[1,5,6,7,8,9,10,11,13,14,15,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,48,49,55,56,80,81,82,83,85,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,156,158,159,160,161,162,163,164,165],
    "COLORTEMP":[5,6,7,8,10,11,14,15,19,20,21,22,23,25,26,28,29,30,31,32,33,34,35,80,82,83,85,129,130,131,132,133,135,136,137,138,139,140,141,142,143,144,145,146,147,153,154,156,158,159,160,161,162,163,164,165],
    "RGB":[6,7,8,21,22,23,30,31,32,33,34,35,131,132,133,137,138,139,140,141,142,143,146,147,153,154,156,158,159,160,161,162,163,164,165],
    "MOTION":[37,49,54],
    "AMBIENT_LIGHT":[37,49,54],
    "WIFICONTROL":[36,37,38,39,40,48,49,51,52,53,54,55,56,57,58,59,61,62,63,64,65,66,67,68,80,81,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,156,158,159,160,161,162,163,164,165],
    "PLUG":[64,65,66,67,68],
    "FAN":[81],
    "MULTIELEMENT":{'67':2}
}

def main(data):
    home_devices = {}
    home_controllers = {}
    switchID_to_homeID = {}
    devices = {}
    rooms = {}
    homes = data['data']
    for h in homes:
        home = h['device']
        home_info = h['device_info']
        if home_info.get('groupsArray',False) and home_info.get('bulbsArray',False) and len(home_info['groupsArray']) > 0 and len(home_info['bulbsArray']) > 0:
            home_id = str(home['id'])
            bulbs_array_length = max([((device['deviceID'] % home['id']) % 1000) + (int((device['deviceID'] % home['id']) / 1000)*256) for device in home_info['bulbsArray']]) + 1
            home_devices[home_id] = [""]*(bulbs_array_length)
            home_controllers[home_id] = []
            for device in home_info['bulbsArray']:
                device_type = device['deviceType']
                device_id = str(device['deviceID'])
                current_index = ((device['deviceID'] % home['id']) % 1000) + (int((device['deviceID'] % home['id']) / 1000)*256)
                home_devices[home_id][current_index] = device_id
                devices[device_id] = {'name':device['displayName'],
                    'mesh_id':current_index,
                    'switch_id':str(device.get('switchID',0)), 
                    'ONOFF': device_type in Capabilities['ONOFF'], 
                    'BRIGHTNESS': device_type in Capabilities["BRIGHTNESS"], 
                    "COLORTEMP":device_type in Capabilities["COLORTEMP"], 
                    "RGB": device_type in Capabilities["RGB"], 
                    "MOTION": device_type in Capabilities["MOTION"], 
                    "AMBIENT_LIGHT": device_type in Capabilities["AMBIENT_LIGHT"], 
                    "WIFICONTROL": device_type in Capabilities["WIFICONTROL"],
                    "PLUG" : device_type in Capabilities["PLUG"],
                    "FAN" : device_type in Capabilities["FAN"],
                    'home_name':home['name'], 
                    'room':'', 
                    'room_name':''
                }
                if str(device_type) in Capabilities['MULTIELEMENT'] and current_index < 256:
                    devices[device_id]['MULTIELEMENT'] = Capabilities['MULTIELEMENT'][str(device_type)]
                if devices[device_id].get('WIFICONTROL',False) and 'switchID' in device and device['switchID'] > 0:
                    switchID_to_homeID[str(device['switchID'])] = home_id
                    devices[device_id]['switch_controller'] = device['switchID']
                    home_controllers[home_id].append(device['switchID'])
            if len(home_controllers[home_id]) == 0:
                for device in home_info['bulbsArray']:
                    device_id = str(device['deviceID'])
                    devices.pop(device_id,'')
                home_devices.pop(home_id,'')
                home_controllers.pop(home_id,'')
            else:
                for room in home_info['groupsArray']:
                    if (len(room.get('deviceIDArray',[])) + len(room.get('subgroupIDArray',[]))) > 0:
                        room_id = home_id + '-' + str(room['groupID'])
                        room_controller = home_controllers[home_id][0]
                        available_room_controllers = [(id%1000) + (int(id/1000)*256) for id in room.get('deviceIDArray',[]) if 'switch_controller' in devices[home_devices[home_id][(id%1000)+(int(id/1000)*256)]]]
                        if len(available_room_controllers) > 0:
                            room_controller = devices[home_devices[home_id][available_room_controllers[0]]]['switch_controller']
                        for id in room.get('deviceIDArray',[]):
                            id = (id % 1000) + (int(id / 1000)*256)
                            devices[home_devices[home_id][id]]['room'] = room_id
                            devices[home_devices[home_id][id]]['room_name'] = room['displayName']
                            if 'switch_controller' not in devices[home_devices[home_id][id]] and devices[home_devices[home_id][id]].get('ONOFF',False):
                                devices[home_devices[home_id][id]]['switch_controller'] = room_controller
                        rooms[room_id] = {'name':room['displayName'],
                            'mesh_id' : room['groupID'], 
                            'room_controller' : room_controller,
                            'home_name' : home['name'], 
                            'switches' : [home_devices[home_id][(i%1000)+(int(i/1000)*256)] for i in room.get('deviceIDArray',[]) if devices[home_devices[home_id][(i%1000)+(int(i/1000)*256)]].get('ONOFF',False)],
                            'isSubgroup' : room.get('isSubgroup',False),
                            'subgroups' : [home_id + '-' + str(subgroup) for subgroup in room.get('subgroupIDArray',[])]
                        }
                for room,room_info in rooms.items():
                    if not room_info.get("isSubgroup",False) and len(subgroups := room_info.get("subgroups",[])) > 0:
                        for subgroup in subgroups:
                            if rooms.get(subgroup,None):
                                rooms[subgroup]["parent_room"] = room_info["name"]
                            else:
                                room_info['subgroups'].pop(room_info['subgroups'].index(subgroup))

    if len(rooms) == 0 or len(devices) == 0 or len(home_controllers) == 0 or len(home_devices) == 0 or len(switchID_to_homeID) == 0:
        print(rooms,devices,home_controllers,home_devices,switchID_to_homeID)
        raise Exception("Error while reading configuration")
    else:
        return {'rooms':rooms, 'devices':devices, 'home_devices':home_devices, 'home_controllers':home_controllers, 'switchID_to_homeID':switchID_to_homeID}

with open("cync_rooms.json","r") as f:
    data=json.load(f)
output = main(data)
print(output)
