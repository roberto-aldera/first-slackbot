import logging
import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

slack_token = os.getenv("SLACK_BOT_TOKEN")
if not slack_token:
    raise ValueError(
        "No Slack Bot Token found. Set the SLACK_BOT_TOKEN environment variable.")

client = WebClient(token=slack_token)


@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    print(data)

    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    event = data.get('event', {})

    if event.get('type') == 'message' and 'subtype' not in event:
        handle_message(event)

    return '', 200


def handle_message(event):
    user = event['user']
    text = event['text']
    channel = event['channel']

    if text.lower().startswith('hi'):
        response = f"Hello, <@{user}>!"
        send_message(channel, response)


@app.route('/slack/commands', methods=['POST'])
def slack_commands():
    data = request.form
    command = data.get('command')
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')

    if command == '/greet':
        return handle_greet_command(channel_id, user_id)

    return '', 200


def handle_greet_command(channel, user):
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=f"Hello, <@{user}>! Hope you're having a great day!"
        )
        return jsonify(response)
    except SlackApiError as e:
        return jsonify({'error': e.response['error']}), 500


def send_message(channel, text):
    try:
        client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        logging.error(f"Error sending message: {e.response['error']}")


if __name__ == '__main__':
    app.run(port=3000, debug=True)
