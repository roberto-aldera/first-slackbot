import logging
import os
from flask import Flask, request, jsonify
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

slack_token = os.getenv("SLACK_BOT_TOKEN")
api_ninjas_token = os.getenv("API_NINJAS_TOKEN")
if not slack_token:
    raise ValueError(
        "No Slack Bot Token found. Set the SLACK_BOT_TOKEN environment variable.")
if not api_ninjas_token:
    raise ValueError(
        "No API Ninjas Token found. Set the API_NINJAS_TOKEN environment variable.")

client = WebClient(token=slack_token)


@app.route('/slack/events', methods=['POST'])
def slack_events():
    """
    Home for all events.
    """
    data = request.json
    print(data)

    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    event = data.get('event', {})

    if event.get('type') == 'message' and 'subtype' not in event:
        handle_message(event)

    return '', 200


def handle_message(event):
    """
    The default response when messaged.
    """
    user = event['user']
    text = event['text']
    channel = event['channel']

    if text.lower().startswith('hi'):
        response = f"Hello, <@{user}>!"
        send_message(channel, response)


@app.route('/slack/commands', methods=['POST'])
def slack_commands():
    """
    Home of all slash commands.
    """
    data = request.form
    command = data.get('command')
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')

    if command == '/greet':
        handle_greet_command(channel_id, user_id)
    if command == '/joke':
        handle_joke_command(channel_id)

    return '', 200

def handle_greet_command(channel, user):
    """
    A simple greeting response.
    """
    greeting = f"Hello, <@{user}>! Hope you're having a great day!"
    send_message(channel, greeting)

def handle_joke_command(channel):
    """
    Joke generator.
    """
    api_url = 'https://api.api-ninjas.com/v1/jokes'
    response = requests.get(api_url, headers={'X-Api-Key': api_ninjas_token}, timeout=5)
    if response.status_code == 200:
        response_json = response.json()
        if response_json:
            send_message(channel, response_json[0]['joke'])
    else:
        print("Error:", response.status_code, response.text)


def send_message(channel, text):
    """
    Wrapper for chat_postMessage handling.
    """
    try:
        client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        logging.error(f"Error sending message: {e.response['error']}")


if __name__ == '__main__':
    app.run(port=3000, debug=True)
