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
slack_client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = slack_client.api_call("auth.test")['user_id']


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    text = str(event.get('text'))
    if text.__contains__("lifestyle"):
        lifestyle_spent=str(getWeeklySum("Lifestyle 🏞️"))
        send_pushover_notification('LIFESTYLE', "You've spent " + lifestyle_spent + " this week")
    if text.__contains__("spendings"):
        spendings_spent=str(getWeeklySum("Spendings 📦"))
        send_pushover_notification('SPENDINGS', "You've spent " + spendings_spent + " this week")
    if text.__contains__("Daily Success"):
        daily_success=str(int(getDailySuccess()*100))
        send_pushover_notification('DAILY_SUCCESS', "You've achieved " + daily_success + "% of your daily goal")
    



if __name__ == "__main__":
    app.run(debug=True, port=8080)

# Functions

def getWeeklySum(category):
    conn = http.client.HTTPSConnection("api.notion.com")
    headers = {
        'Authorization': 'Bearer ' + os.environ['NOTION_API_TOKEN'],
        'Notion-Version': '2021-08-16',
        'Content-Type': 'application/json'
    }
    first_day_of_week = (datetime.now() - timedelta(days=datetime.today().weekday()) - timedelta(days=1)).isoformat()
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

def getDailySuccess():
    conn = http.client.HTTPSConnection("api.notion.com")
    headers = {
        'Authorization': 'Bearer ' + os.environ['NOTION_API_TOKEN'],
        'Notion-Version': '2021-08-16',
        'Content-Type': 'application/json'
    }
    today = (datetime.now()).isoformat()
    intended_payload = {
        'filter': {
            'and': [
                {
                    'property': 'Date',
                    'date': {
                        'on_or_after': today,
                    },
                },
            ],
        },
    }
    reality_payload = {
        'filter': {
            'and': [
                {
                    'property': 'Date',
                    'date': {
                        'on_or_after': today,
                    },
                },
            ],
        },
    }
    conn.request('POST', f'/v1/databases/' + os.environ['DATABASE_ID'] + '/query', body=json.dumps(intended_payload), headers=headers)
    res = conn.getresponse()
    intended_data = res.read()
    intended_data_json = json.loads(intended_data.decode('utf-8'))

    conn.request('POST', f'/v1/databases/' + os.environ['DATABASE_ID'] + '/query', body=json.dumps(reality_payload), headers=headers)
    res = conn.getresponse()
    reality_data = res.read()
    reality_data_json = json.loads(reality_data.decode('utf-8'))

    if 'results' in intended_data_json and 'results' in reality_data_json:
        intended_sum = sum(item['properties']['Amount']['number'] for item in intended_data_json['results'] if 'Amount' in item['properties'])
        reality_sum = sum(item['properties']['Amount']['number'] for item in reality_data_json['results'] if 'Amount' in item['properties'])
        result = float(reality_sum) / float(intended_sum)
        return(result)
    else:
        print("Error:", intended_data_json, reality_data_json)

def send_pushover_notification(subject, message):
    url = 'https://api.pushover.net/1/messages.json'
    payload = {'token': os.environ[subject + '_API_TOKEN'], 'user': os.environ['PUSHOVER_USER_KEY'], 'message': message}
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print('Notification sent')
    else:
        print(f"Failed to send notification, status code: {r.status_code}")

#End of functions