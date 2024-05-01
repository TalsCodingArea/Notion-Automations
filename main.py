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
    category = text.split()[0] + " " + text.split()[1]
    person = text.split()[2] + " " + text.split()[3]
    if text.__contains__("Daily Success"):
        daily_success=str(int(getDailySuccess()*100))
        send_pushover_notification('DAILY_SUCCESS', "You've achieved " + daily_success + "% of your daily goal")
    else:
        pushover_key = (text.split()[2] + "_" + text.split()[0]).upper()
        spendings_spent=str(getWeeklySum(category, person))
        send_pushover_notification(pushover_key, "You've spent " + spendings_spent + " this week", person)
    



if __name__ == "__main__":
    app.run(debug=True, port=8080)

# Functions

def getWeeklySum(category, person):
    conn = http.client.HTTPSConnection("api.notion.com")
    headers = {
        'Authorization': 'Bearer ' + os.environ['NOTION_API_TOKEN'],
        'Notion-Version': '2021-08-16',
        'Content-Type': 'application/json'
    }
    first_day_of_week = (datetime.now() - timedelta(days=datetime.today().weekday())).isoformat()
    payload = {
        "filter":{
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
                {
                    'property': 'Tag',
                    'multi_select': {
                        'contains': person,
                    },
                }
            ],
        }
    }
    response = requests.post("https://api.notion.com/v1/databases/" + os.environ['DATABASE_ID'] + '/query', headers=headers, data=json.dumps(payload))
    data = response.json()
    if 'results' in data:
        results = data['results']
        amount_sum = sum(item['properties']['Amount']['number'] for item in results if 'Amount' in item['properties'])
        amount_sum = int(amount_sum*100)
        amount_sum = float(amount_sum)/100
        return (amount_sum)
    else:
        print("Error:", data)

def getDailySuccess():
    conn = http.client.HTTPSConnection("api.notion.com")
    headers = {
        'Authorization': 'Bearer ' + os.environ['NOTION_API_TOKEN'],
        'Notion-Version': '2021-08-16',
        'Content-Type': 'application/json'
    }
    today = (datetime.now()).isoformat().split('T')[0]
    
    payload = {
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

    conn.request('POST', f'/v1/databases/' + os.environ['DAILY_DATABASE_ID'] + '/query', body=json.dumps(payload), headers=headers)
    res = conn.getresponse()
    data = res.read()
    data_json = json.loads(data.decode('utf-8'))

    if 'results' in data_json:
        intended_sum = sum(item['properties']['Intended Study']['number'] for item in data_json['results'] if 'Intended Study' in item['properties'])
        reality_sum = sum(item['properties']['Reality Study']['number'] for item in data_json['results'] if 'Reality Study' in item['properties'])
        result = float(reality_sum) / float(intended_sum)
        return(result)
    else:
        print("Error:", data_json)

def send_pushover_notification(subject, message, person):
    url = 'https://api.pushover.net/1/messages.json'
    if person == "All":
        payload = {'token': os.environ[subject + '_API_TOKEN'], 'user': os.environ['PUSHOVER_USER_KEY'], 'message': message, 'device': "iPhone"}
    else:
        payload = {'token': os.environ[subject + '_API_TOKEN'], 'user': os.environ['PUSHOVER_USER_KEY'], 'message': message, 'device': "Shiri_iphon"}
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print('Notification sent')
    else:
        print(f"Failed to send notification, status code: {r.status_code}")

#End of functions

