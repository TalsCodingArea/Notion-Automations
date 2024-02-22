from pathlib import Path
from dotenv import load_dotenv
import slack
import os
import requests
import json
import http.client
from flask import Flask, request, make_response, Response
from slackeventsapi import SlackEventAdapter
from notion_client import Client
from datetime import datetime, timedelta
from twilio.rest import Client

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

twilio_client = Client(os.environ['ACCOUNT_SID'], os.environ['TWILIO_TOKEN'])
slack_client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = slack_client.api_call("auth.test")['user_id']

def getWeeklySum(category):
    conn = http.client.HTTPSConnection("api.notion.com")
    headers = {
        'Authorization': 'Bearer ' + os.environ['NOTION_API_TOKEN'],
        'Notion-Version': '2021-08-16',
        'Content-Type': 'application/json'
    }
    first_day_of_week = (datetime.now() - timedelta(days=datetime.today().weekday())).isoformat()
    payload = {
        'filter': {
            'and': [
                {
                    'property': 'Category',
                    'multi_select': {
                        'contains': category,
                    },
                },
                {
                    'property': 'Date',
                    'date': {
                        'on_or_after': first_day_of_week,
                    },
                },
            ],
        },
    }
    conn.request('POST', f'/v1/databases/' + os.environ['DATABASE_ID'] + '/query', body=json.dumps(payload), headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    data_json = json.loads(data.decode('utf-8'))

    if 'results' in data_json:
        amount_sum = sum(item['properties']['Amount']['number'] for item in data_json['results'] if 'Amount' in item['properties'])
        return(amount_sum)
    else:
        print("Error:", data_json)

    '''
    notion=Client(auth=os.environ['NOTION_API_TOKEN'])
    sum=0
    first_day_of_week = (datetime.now() - timedelta(days=datetime.today().weekday())).isoformat()
    filter_params = {
        "database_id": os.environ['DATABASE_ID'],
        "filter": {
            "and": [
                {
                    property: "Date",
                    "date": {
                        "on_or_after":first_day_of_week
                    }
                },
                {
                    property: 'Category',
                    "multi_select": {
                        "contains": category
                    }
                }
            ]
        }
    }
    filtered_pages = notion.databases.query(filter_params)
    for page in filtered_pages['results']:
        if "Amount" in page['properties'].keys():
            property_value = page['properties']["Amount"]['number']
            sum+=property_value
    '''



@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = str(event.get('text'))
    lifestyle_spent=str(getWeeklySum("Lifestyle 🏞️"))
    spendings_spent=str(getWeeklySum("Spendings 📦"))
    message = twilio_client.messages.create(
        body="So far this week you've spent " + lifestyle_spent + " on lifestyle🏞️, and " + spendings_spent + " on spendings📦",
        from_=os.environ['TWILIO_NUMBER'],
        to=os.environ['TARGET_NUMBER']
    )



if __name__ == "__main__":
    app.run(debug=True, port=8080)

