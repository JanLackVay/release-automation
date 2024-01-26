import json

import requests
import yaml
from check_car_policy import main as check_car_policy


def main():
    message = check_car_policy()

    if "ts" in message or "ve" in message:
        message = message + "\n" + "FYI"
        if "ve-0" in message:
            message = message + "\n" + "@U02JU20LKB9>"  # Christoph Siebold
        if "us" in message:
            message = message + "\n" + "<@U02V78AU64T>"  # Martin Kuckcuck
    slack_webhook_url = yaml.safe_load(open("../credentials.yaml", "r"))[
        "configuration_alert_url"
    ]

    message_payload = {"text": message}
    headers = {"Content-type": "application/json"}
    response = requests.post(
        slack_webhook_url, data=json.dumps(message_payload), headers=headers
    )

    print(response)


if __name__ == "__main__":
    main()
