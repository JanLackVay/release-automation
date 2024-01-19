import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def send_slack_message(token, channel, message):
    client = WebClient(token=token)

    try:
        response = client.chat_postMessage(channel=channel, text=message)
        print(f"Message sent to {channel}: {response['ts']}")
    except SlackApiError as e:
        print(f"Error sending message to {channel}: {e.response['error']}")


# Set your Slack API token and channel
slack_token = "YOUR_SLACK_API_TOKEN"
slack_channel = "#general"  # Replace with your channel name

# Message to send
message_text = "Hello World!"

# Call the function to send the message
send_slack_message(slack_token, slack_channel, message_text)
