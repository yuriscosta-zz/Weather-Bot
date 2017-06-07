'''
This is a Messenger bot that shows some information about the current weather
in the user shared location.
'''

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
