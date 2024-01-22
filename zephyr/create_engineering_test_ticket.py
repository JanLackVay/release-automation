import argparse
import json

import requests
import yaml
from atlassian import Jira

URL = "https://vayio.atlassian.net/rest/api/2/issue"


def main():
    username = yaml.safe_load(open("credentials.yaml"))["user_name"]
    api_token = yaml.safe_load(open("credentials.yaml"))["jira_api_token"]

    # Construct the basic authentication string
    auth = HTTPBasicAuth(username, api_token)

    payload_items = {
        "test_steps": "customfield_10058",  # to add test steps we need to add the steps to this field response.json()['fields']['customfield_10058']
        "components_id": "10181",  # ['fields']['components']['id']
        "assignee_id": "617969efe79ff6006fae4f89",  # ['fields']['assignee'] Chris Siebdold
        "engineering_test_ticket_id": "10024",  # ['fields']['issuetype']['id'] engineering test ticket
        "responsible_engineer_id": "61ad43e1c510bc006b3458c4",  # ['fields']['customfield_10052']['accountId'] Jan Lack
        "responsible_engineer": "customfield_10052",
        "sd_required": "customfield_10053",
        "td_required": "customfield_10054",
        "preferred_test_date": "customfield_10055",
        "estimated_length": "customfield_10059",
        "additional_notes": "customfield_10060",
        "expected_test_result": "customfield_10062",
        "test_location": "customfield_10571",
        "p_0": "1",
        "engineering_test_ticket_title": "Engineering Test Ticket",
    }

    create_ett(auth, payload_items)


def create_ett(auth, payload_items):
    url = "https://vayio.atlassian.net/rest/api/2/issue"

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = json.dumps(
        {
            "fields": {
                "components": [{"id": components_id}],
                "summary": engineering_test_ticket_title,
                "issuetype": {"id": engineering_test_ticket_id},
                "priority": {"id": p_0},
                "project": {"key": "REE"},
                test_steps: test_description,
                responsible_engineer: {"accountId": responsible_engineer_id},
                sd_required: {"value": "1 SD", "id": "10335"},
                td_required: {"value": "1 TD", "id": "10338"},
                preferred_test_date: "-",
                estimated_length: "-",
                additional_notes: "-",
                expected_test_result: "-",
                test_location: {"value": "Tegel Testing Grounds", "id": "11556"},
            },
        }
    )

    response = requests.request("POST", url, data=payload, headers=headers, auth=auth)
