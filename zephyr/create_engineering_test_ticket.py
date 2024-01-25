import argparse
import json

import requests
import yaml
from requests.auth import HTTPBasicAuth

URL = "https://vayio.atlassian.net/rest/api/2/issue"


def main(
    vsr_version: str,
    vdrive_version: str,
    vreecu_assets: dict[str, str],
    depb_assets: dict[str, str],
    sec_ve_assets: dict[str, str],
    cycle_information: dict[str, str],
    regression: bool == False,
    parent_epic_id: str,
):
    sec_ts_version = "1.15.0"
    username = yaml.safe_load(open("credentials.yaml"))["user_name"]
    api_token = yaml.safe_load(open("credentials.yaml"))["jira_api_token"]

    # Construct the basic authentication string
    auth = HTTPBasicAuth(username, api_token)

    test_steps = "customfield_10058"  # to add test steps we need to add the steps to this field response.json()['fields']['customfield_10058']
    components_id = "10181"  # ['fields']['components']['id']
    assignee_id = "617969efe79ff6006fae4f89"  # ['fields']['assignee'] Chris Siebdold
    assigned_mail = "christoph.siebold@vay.io"  # ['fields']['assignee']['emailAddress']
    engineering_test_ticket_id = (
        "10024"  # ['fields']['issuetype']['id'] engineering test ticket
    )
    else:
        payload_items["engineering_test_ticket_title"] = f"release {vdrive_version}"
        payload_items[
            "test_description"
        ] = f"""Please follow this test cycle: https://vayio.atlassian.net/projects/REE?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/testPlayer/{cycle_information["vdrive"]["key"]}
        Starting with {vdrive_version}"""

    return create_ett(auth, payload_items)


def create_ett(auth, payload_items):
    url = "https://vayio.atlassian.net/rest/api/2/issue"

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = json.dumps(
        {
            "fields": {
                "parent": {"id": payload_items["parent_id"]},
                "components": [{"id": payload_items["components_id"]}],
                "summary": payload_items["engineering_test_ticket_title"],
                "issuetype": {"id": payload_items["engineering_test_ticket_id"]},
                "priority": {"id": payload_items["p_0"]},
                "project": {"key": "REE"},
                payload_items["test_steps"]: payload_items["test_description"],
                payload_items["responsible_engineer"]: {
                    "accountId": payload_items["responsible_engineer_id"]
                },
                payload_items["sd_required"]: {"value": "1 SD", "id": "10335"},
                payload_items["td_required"]: {"value": "1 TD", "id": "10338"},
                payload_items["preferred_test_date"]: "-",
                payload_items["estimated_length"]: "-",
                payload_items["additional_notes"]: "-",
                payload_items["expected_test_result"]: "-",
                payload_items["test_location"]: {
                    "value": "Tegel Testing Grounds",
                    "id": "11556",
                },
            },
        }
    )

    response = requests.request("POST", url, data=payload, headers=headers, auth=auth)
    return response.json()


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
    parser.add_argument(
        "--vreecu-assets",
        type=dict[str, str],
        help="vREECU assets dict[tag, asset_link]",
    )
    parser.add_argument(
        "--depb-assets",
        type=dict[str, str],
        help="DEPB assets dict[tag, asset_link].",
    )
    parser.add_argument(
        "--sec-assets",
        type=dict[str, str],
        help="SEC assets dict[tag, asset_link].",
    )
    parser.add_argument(
        "--cycle-information",
        type=dict[str, str],
        help="Cycle information.",
    )
    parser.add_argument(
        "--regression",
        type=lambda x: x.lower() == "true",
        help="If regression test cycle should be created true, else false.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
