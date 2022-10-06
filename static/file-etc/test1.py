""" x = {'destination': 'U452d6a87910fad5c9d45e68322721e25', 'events': [{'type': 'message', 'message': {'type': 'image', 'id': '15668787552023', 'contentProvider': {'type': 'line'}, 'imageSet': {
    'id': 'A689761B1B345C9272912F54C76D9C96326AE7A4934D2D3839AA96CBF438D953', 'index': 1, 'total': 3}}, 'timestamp': 1646107733297, 'source': {'type': 'user', 'userId': 'U2f4de7b2fdcad58b356c45cd5f3e5be8'}, 'replyToken': '13776c6609b2423a87d59cbd44190414', 'mode': 'active'}]
    }
y = {'destination': 'U452d6a87910fad5c9d45e68322721e25', 'events': [{'type': 'message', 'message': {'type': 'image', 'id': '15669625849391', 'contentProvider': {
    'type': 'line'}}, 'timestamp': 1646118108588, 'source': {'type': 'user', 'userId': 'U2f4de7b2fdcad58b356c45cd5f3e5be8'}, 'replyToken': 'c2a4ab27b8cd4a01b8a410b0cc38fbe5', 'mode': 'active'}]}


q = x['events'][0]['message']['imageSet']['total']
print(q)
 """

""" import uuid
print(type(uuid.uuid4()))
 """
""" import requests
import json
response_API = requests.get('https://5982-2001-fb1-be-84da-6084-f161-15f4-3974.ngrok.io/city?filepath=B29A059B985D3BA7C29A703BE06E01542964E2AF33E2CF89F4E9A2E580267CEA')
data_res = response_API.text
#data_api = json.loads(data_res) 
print(data_res) """

""" import requests
response_API = requests.get('https://5d10-1-4-149-0.ngrok.io/city?filepath={}'.format("B29A059B985D3BA7C29A703BE06E01542964E2AF33E2CF89F4E9A2E580267CEA"))
print(response_API.text) """

