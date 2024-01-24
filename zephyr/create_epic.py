import argparse
import json

import requests
import yaml
from requests.auth import HTTPBasicAuth

URL = "https://vayio.atlassian.net/rest/api/2/issue"


def main(vsr_version: str == None, vdrive_version: str):
    username = yaml.safe_load(open("credentials.yaml"))["user_name"]
    api_token = yaml.safe_load(open("credentials.yaml"))["jira_api_token"]

    # Construct the basic authentication string
    auth = HTTPBasicAuth(username, api_token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload_items = {
        "assignee_id": "61ad43e1c510bc006b3458c4",  # ['fields']['assignee'] Jan Lack
        "epic_id": "10000",  # ['fields']['issuetype']['id'] Epic
        "epci_name": "customfield_10011",  # ['fields']['customfield_10011'] EPCI Name
        "additional_notes": "customfield_10060",
        "expected_test_result": "customfield_10062",
        "test_location": "customfield_10571",
        "p_0": "1",
        "epic_title": f"VSR-{vsr_version}",
        "labels": [f"VSR-{vsr_version}"],
    }

    if vsr_version:
        payload_items["labels"] = [f"VSR-{vsr_version}"]
        payload_items["epic_title"] = f"VSR-{vsr_version}"
    else:
        payload_items["labels"] = [f"release-{vdrive_version}"]
        payload_items["epic_title"] = f"release-{vdrive_version}"

    payload = json.dumps(
        {
            "fields": {
                "summary": payload_items["epic_title"],
                "issuetype": {"id": payload_items["epic_id"]},
                "priority": {"id": payload_items["p_0"]},
                "project": {"key": "REE"},
                "assignee": {"account_id": payload_items["assignee_id"]},
                "labels": payload_items["labels"],
            },
        }
    )

    response = requests.request(
        "POST", URL, data=payload, headers=headers, auth=auth
    ).json()

    return response["id"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--vsr-version",
        type=str,
        help="VSR version: <major>.<minor>.<patch>",
    )
    parser.add_argument(
        "--vdrive-version",
        type=str,
        required=True,
        help="vDrive version. <major>.<minor>.<patch> If only vDrive test cycle should be created, use just this argument.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
