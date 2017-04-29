#coding:utf-8

import os
import requests
import traceback
import json

from flask import Flask, request

token = os.environ.get('FB_ACCESS_TOKEN')
api_token = os.environ.get('WEATHER_API_KEY')
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def webhook():
	if request.method == 'POST':
		try:
			data = json.loads(request.data.decode())
			print data
			message = data['entry'][0]['messaging'][0]['message']
			#text = data['entry'][0]['messaging'][0]['message']['text']
			sender = data['entry'][0]['messaging'][0]['sender']['id']

			if 'attachments' in message:
				if 'payload' in message['attachments'][0]:
					if 'coordinate' in message['attachments'][0]['payload']:
						location = message['attachments'][0]['payload']['coordinate']
						latitude = location['lat']
						longitude = location['long']
						url = 'http://api.openweathermap.org/data/2.5/weather?' \
						'lat={}&lon={}&appid={}&units={}&lang={}'.format(latitude, longitude, api_key, 'metric', 'pt')
						r = requests.get(url) 
						description = r.json()['weather'][0]['description'].title()
						icon = r.json()['weather'][0]['icon']
						weather = r.json()['main']

						text_res = '{}\n' \
								   'Temperatura: {}\n' \
								   'Pressão: {}\n' \
								   'Umidade: {}\n' \
								   'Máxima: {}\n' \
								   'Mínima: {}'.format(description, weather['temp'], weather['pressure'], weather['humidity'], 
								   	weather['temp_max'], weather['temp_min'])

						payload = {'recipient': {'id': sender}, 'message': {'text': text_res}}

						r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, json=payload)

 			else:
				text = message['text']
				payload = location_quick_reply(sender)
				r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token' + str(token), json=payload)
		
		except Exception as e:
			print(traceback.format_exc())
	
	elif request.method == 'GET':
		print request.args.get('hub.verify_token')
		print os.environ.get('FB_VERIFY_TOKEN') 
		if request.args.get('hub.verify_token') == os.environ.get('FB_VERIFY_TOKEN') :
				return request.args.get('hub.challenge')		
		return "Wrong Verify Token"
	
	return "Nothing"

def location_quick_reply(sender):
	return {
		"recipient": {
			"id": sender
		}, 
		"message": {
			"text": "Compartilhe sua localização:",
			"quick_replies": [
				{
					"content-type": "location",
				}
			]
		}

	}

if __name__ == '__main__':
	app.run(debug=True)