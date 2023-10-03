import requests
import json
hook = 'https://chatapi.viber.com/pa/set_webhook'
headers = {'X-Viber-Auth-Token': 'YOUR_TOKEN' }
sen = dict(url='https://faf5-188-163-102-40.ngrok-free.app/viber/',
           event_types = ['unsubscribed', 'conversation_started', 'message', 'delivered', 'subscribed'])
r = requests.post(hook, json.dumps(sen), headers=headers)
print(r.json())