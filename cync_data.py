import aiohttp
import asyncio
import json

API_AUTH = "https://api.gelighting.com/v2/user_auth"
API_REQUEST_CODE = "https://api.gelighting.com/v2/two_factor/email/verifycode"
API_2FACTOR_AUTH = "https://api.gelighting.com/v2/user_auth/two_factor"
API_DEVICES = "https://api.gelighting.com/v2/user/{user}/subscribe/devices"

async def authenticate(username, password):
    """Authenticate with the API and get a token."""
    auth_data = {'corp_id': "1007d2ad150c4000", 'email': username, 'password': password}
    async with aiohttp.ClientSession() as session:
        async with session.post(API_AUTH, json=auth_data) as resp:
            response = await resp.json()
            if resp.status == 200:
                return (response)
            else:
                request_code_data = {'corp_id': "1007d2ad150c4000", 'email': username, 'local_lang': "en-us"}
                async with aiohttp.ClientSession() as session:
                    async with session.post(API_REQUEST_CODE,json=request_code_data) as resp:
                        if resp.status == 200:
                            two_factor_code = input("Enter 2 Factor Code:")
                            two_factor_data = {'corp_id': "1007d2ad150c4000", 'email': username,'password': password, 'two_factor': two_factor_code, 'resource':"abcdefghijklmnop"}
                            async with aiohttp.ClientSession() as session:
                                async with session.post(API_2FACTOR_AUTH,json=two_factor_data) as resp:
                                    response = await resp.json()
                                    return (response)
                        else:
                            print("failed to authorize")

async def get_devices(auth_token, user):
    """Get a list of devices for a particular user."""
    headers = {'Access-Token': auth_token}
    async with aiohttp.ClientSession() as session:
        async with session.get(API_DEVICES.format(user=user), headers=headers) as resp:
            response  = await resp.json()
            return response

async def get_properties(auth_token, product_id, device_id):
    """Get properties for a single device."""
    API_DEVICE_INFO = "https://api.gelighting.com/v2/product/{product_id}/device/{device_id}/property"
    headers = {'Access-Token': auth_token}
    async with aiohttp.ClientSession() as session:
        async with session.get(API_DEVICE_INFO.format(product_id=product_id, device_id=device_id), headers=headers) as resp:
            response = await resp.json()
            return response

async def main():
    username = input("username:")
    password = input("password:")
    user_auth = await authenticate(username, password)
    access_token = user_auth['access_token']
    user_id = user_auth['user_id']
    with open("cbyge_user_info.json","w") as file:
        file.write(json.dumps(user_auth,indent=4))
    devices = await get_devices(access_token, user_id)
    rooms = []
    for device in devices:
        device_info = await get_properties(access_token, device['product_id'], device['id'])
        if 'groupsArray' in device_info and len(device_info['groupsArray']) > 0:
            rooms.append(device_info)
    with open("cbyge_rooms.json","w") as file:
        file.write(json.dumps({'data': rooms},indent=4))
    print("finished getting devices, check cbyge_rooms.json for results")

asyncio.run(main())
