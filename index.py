#coding:utf-8

import os
import requests
import traceback
import json

from flask import Flask, request

token = os.environ.get('FB_ACCESS_TOKEN')
api_key = os.environ.get('WEATHER_API_KEY')
app = Flask(__name__)


def location_quick_reply(sender):
	return {'recipient': {'id': sender}, 'message': {'text': "Can you share your location? I'll give you some details about the weather. :D"}}


def send_message(payload):
	requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, json=payload)


def send_attachment(sender, type, payload):
	return {
		"recipient": {
			"id": sender
		},
		"message": {
			"attachment": {
				"type": type,
				"payload": payload
			}
		} 
	}


def send_text(sender, text):
	return {
		"recipient": {
			"id": sender
		},
		"message": {
			"text": text
		} 
	}


def send_weather_info(sender, **kwargs):
	lat = kwargs.pop('lat', None)
	lon = kwargs.pop('lon', None)

	if lat and lon:
		query = 'lat={}&lon={}'.format(lat, lon)

	url = 'http://api.openweathermap.org/data/2.5/weather?' \
	      '{}&appid={}&units={}&lang={}'.format(query, 
	      								        api_key, 
	      								        'metric', 
	      								        'en')

	r = requests.get(url)
	response = r.json()

	print (response)

	if 'cod' in response:
		if response['cod'] != 200:
			return 'error'

	name = response['name']
	weather = response['main']
	wind = response['wind']

	elements = [{
		'title':  name,
		'subtitle': 'Temperature: {} degrees'.format(str(weather['temp']).replace('.', ',')),
		'image_url': 'https://cdn-images-1.medium.com/max/800/1*LkbHjhacSRDNDzupX7pgEQ.jpeg'
	}]

	for info in response['weather']:
		description = info['description'].capitalize()
		icon = info['icon']

		weather_data = 'Pressure: {}\n' \
					   'Humidity: {}\n' \
					   'Max: {}\n' \
					   'Min: {}'.format(weather['pressure'], weather['humidity'], 
								   		weather['temp_max'], weather['temp_min'])

		if 'visibility' in response:
			weather_data = '{}\n Visibility: {}'.format(weather_data, response['visibility'])

		elements.append({
			'title': description,
			'subtitle': weather_data,
			'image_url': 'http://openweathermap.org/img/w/{}.png'.format(icon)
		})

	payload = send_attachment(sender,
                              'template',
                              {
                              	"template_type": "list",
                                "top_element_style": "large",
                                "elements": elements,
                                #"buttons": [
                                #	{
                                #        "title": "Fazer nova pesquisa",
                                #        "type": "postback",
                                #        "payload": "do_it_again"
                                #    }
                                #]
                              })

	send_message(payload)
	return None

@app.route('/', methods=['GET', 'POST'])
def webhook():
	if request.method == 'POST':
		try:
			data = json.loads(request.data.decode())
			sender = data['entry'][0]['messaging'][0]['sender']['id']
			
			print(data)

			if 'message' in data['entry'][0]['messaging'][0]:
				message = data['entry'][0]['messaging'][0]['message']

			if 'attachments' in message:
				if 'payload' in message['attachments'][0]:
					if 'coordinates' in message['attachments'][0]['payload']:
						location = message['attachments'][0]['payload']['coordinates']
						lat = location['lat']
						lon = location['long']
							
						#send_weather_info(sender, lat=lat, lon=lon)
						send_weather_info(sender, lat=lat, lon=lon)
						if _return == 'error':
							message = send_text(sender, get_message('error'))
							send_message(message)

							payload = location_quick_reply(sender)
							send_message(payload)

						'''
						url = 'http://api.openweathermap.org/data/2.5/weather?' \
						'lat={}&lon={}&appid={}&units={}&lang={}'.format(latitude, longitude, api_key, 'metric', 'en')
						r = requests.get(url) 
						description = r.json()['weather'][0]['description'].title()
						icon = r.json()['weather'][0]['icon']
						weather = r.json()['main']
							text_res = '{}\n' \
								   'Temperature: {}\n' \
								   'Pressure: {}\n' \
								   'Humidity: {}\n' \
								   'Max: {}\n' \
								   'Min: {}'.format(description, weather['temp'], weather['pressure'], weather['humidity'], 
								   	weather['temp_max'], weather['temp_min'])

						payload = {'recipient': {'id': sender}, 'message': {'text': text_res}}
							
						print(payload)
							
						send_message(payload)
						'''

	 		else:
				payload = location_quick_reply(sender)
				
				print(payload)
				
				send_message(payload)

		except Exception as e:
			print(traceback.format_exc())
	
	elif request.method == 'GET':
		print request.args.get('hub.verify_token')
		print os.environ.get('FB_VERIFY_TOKEN')

		if request.args.get('hub.verify_token') == os.environ.get('FB_VERIFY_TOKEN'):
				return request.args.get('hub.challenge')		
		return "Wrong Verify Token"
	
	return "Nothing"


if __name__ == '__main__':
	app.run(debug=True)