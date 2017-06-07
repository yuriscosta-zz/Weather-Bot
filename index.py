'''
This is a Messenger bot that shows some information about the current weather
in the user shared location.
'''

# pylint: disable=E0401
# pylint: disable=C0103
# pylint: disable=E0602
# coding:utf-8

import os
import traceback
import json
import requests

from flask import Flask, request

TOKEN = os.environ.get('FB_ACCESS_TOKEN')
API_KEY = os.environ.get('WEATHER_API_KEY')
app = Flask(__name__)


def location_quick_reply(sender):
    '''
    Returns a json with the user's id and a message
	Keyword argument:
	sender -- user's id
	'''
    return {
        'recipient': {
            'id': sender
        },
        'message': {
            'text': "Can you share your location? I'll give you \
                     some details about the weather. :D"
        }
    }


def send_message(payload):
    '''
	Will send to the chat what you pass as argument
	Keyword argument
	payload -- a message or a json with data
	'''
    requests.post('https://graph.facebook.com/v2.6/me/messages/? \
	               access_token=' + TOKEN, json=payload)


def send_attachment(sender, attach_type, payload):
    '''
    Sends to the chat a couple of data passed as an attachment
    Keyword arguments:
    sender -- user's id
    attach_type -- the type of the attachment
    payload -- a message or a json with data
    '''
    return {
        "recipient": {
            "id": sender
        },
        "message": {
            "attachment": {
                "type": attach_type,
                "payload": payload
            }
        }
    }


def send_text(sender, text):
    '''
    Returns a json with the user's id and a text passed
	Keyword arguments:
	sender -- user's id
	text -- message content
	'''
    return {
        "recipient": {
            "id": sender
        },
        "message": {
            "text": text
        }
    }


def send_weather_info(sender, lat, lon):
    '''
	Sends the information about the shared weather
	Keyword arguments:
	sender -- user's id
	lat -- latitude
	lon -- longitude
    '''

    if lat and lon:
        query = 'lat={}&lon={}'.format(lat, lon)
        url = 'http://api.openweathermap.org/data/2.5/weather? \
	           {}&appid={}&units={}&lang={}'.format(query, API_KEY, 'metric', 'en')

    data = requests.get(url)
    response = data.json()
    print(response)

    if 'cod' in response:
        if response['cod'] != 200:
            return 'error'

    name = response['name']
    weather = response['main']

    elements = [{
        'title':  name,
        'subtitle': 'Temperature: {} degrees'.format(str(weather['temp']).replace('.', ',')),
        'image_url': 'https://cdn-images-1.medium.com/max/800/1*LkbHjhacSRDNDzupX7pgEQ.jpeg'
    }]

    for info in response['weather']:
        description = info['description'].capitalize()
        icon = info['icon']
        weather_data = 'Pressure: {}\n \
					    Humidity: {}\n \
					    Max: {}\n \
					    Min: {}'.format(weather['pressure'], weather['humidity'],
                         weather['temp_max'], weather['temp_min'])

        if 'visibility' in response:
            weather_data = '{}\n Visibility: {}'.format(weather_data, response['visibility'])

        elements.append({
            'title': description,
            'subtitle': weather_data,
            'image_url': 'http://openweathermap.org/img/w/{}.png'.format(icon)
        })

    payload = send_attachment(sender, 'template', {"template_type": "list",
                                                   "top_element_style": "large",
                                                   "elements": elements,})

    send_message(payload)
    return None


@app.route('/', methods=['GET', 'POST'])
def webhook():
    '''
    Deals with all the interaction between the user and the bot
    '''
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

                        send_weather_info(sender, lat=lat, lon=lon)
                        if _return == 'error':
                            message = send_text(sender, get_message('error'))
                            send_message(message)

                            payload = location_quick_reply(sender)
                            send_message(payload)

            else:
                payload = location_quick_reply(sender)
                print(payload)
                send_message(payload)

        except Exception:
            print(traceback.format_exc())

    elif request.method == 'GET':
        print(request.args.get('hub.verify_token'))
        print(os.environ.get('FB_VERIFY_TOKEN'))

        if request.args.get('hub.verify_token') == os.environ.get('FB_VERIFY_TOKEN'):
            return request.args.get('hub.challenge')
        return "Wrong Verify Token"

    return "Nothing"


if __name__ == '__main__':
    app.run(debug=True)
