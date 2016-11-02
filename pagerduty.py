import json
import urllib2
import requests

API_ACCESS_KEY = 'b4e13bfcdecf4732bc9decb75aeafe9c'

def notify_pagerduty():
    headers = {
        'Authorization': 'Token token={0}'.format(API_ACCESS_KEY),
        'Content-type': 'application/json',
    }
    payload = json.dumps({
      "service_key": API_ACCESS_KEY,
      "event_type": "trigger",
      "description": "Rate Limit Reached!"
    })
    print "Sending to Pagerduty",payload
    r = requests.post(
                    'https://events.pagerduty.com/generic/2010-04-15/create_event.json',
                    headers=headers,
                    data=payload,
    )
    print "Done!"


if __name__ == '__main__':
    notify_pagerduty()

