import json

import requests

from check_car_policy import main as check_car_policy


def main():
    message = check_car_policy()

    if "ts" in message or "ve" in message:
        message = message + "\n" + "FYI"
        if "ve-0" in message:
            message = message + "\n" + "FYI <@D033PRP2KPF>"
        if "us" in message:
            message = message + "\n" + "FYI <@D02VA0VT6A2>"

    slack_webhook_url = "https://hooks.slack.com/services/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"

    message_payload = {"text": message}
    headers = {"Content-type": "application/json"}
    response = requests.post(
        slack_webhook_url, data=json.dumps(message_payload), headers=headers
    )

    print(response)


if __name__ == "__main__":
    main()
