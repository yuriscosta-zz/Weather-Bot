# Weather Bot
This Messenger bot shows some information about the current weather in the user shared location. All the credits to [this tutorial](https://blog.mbeck.com.br/tutorial-chatbot-facebook-messenger-cd59d8e700d6).

# Installation
Clone this repository. Install the requirements.

    pip install requirements.txt

Add this environments variables.

    WEATHER_API_KEY # OpenWeatherMap.org api token
    FB_VERIFY_TOKEN # Facebook Messenger webhook verify token (Webhook settings panel)
    FB_ACCESS_TOKEN # Facebook Messenger access token

Run Flask web server.

    python index.py
    
# Built With
* Python
* Flask

# Privacy Policy
This app do not store any data of any user in any server.

# License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/yuriscosta/Weather-Bot/blob/master/LICENSE) file for details
