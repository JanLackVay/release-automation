import argparse
import json

import requests
import yaml

URL = "https://vayio.atlassian.net/rest/api/2/issue"


def main(
    vsr_version: str,
    vdrive_version: str,
    vreecu_version,
    depb_version: str,
    sec_ts_version: str,
    sec_ve_version: str,
):
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
    payload_items[
        "test_description"
    ] = f"""vREECU {vreecu_version}: [https://github.com/Reemote/ree-reecu/releases/download/R{vreecu_version}/release_artifacts.zip|https://github.com/Reemote/ree-reecu/releases/download/R{vreecu_version}/release_artifacts.zip]\n
        vDrive *v{vdrive_version}*\n
        SEC: VE v{sec_ve_version} [https://github.com/Reemote/ree-reecu-sec/releases/download/v3.2.0/sec_ve-v3.2.0-0b85da4.jed|https://github.com/Reemote/ree-reecu-sec/releases/download/v3.2.0/sec_ve-v3.2.0-0b85da4.jed]
        SEC: TS v{sec_ts_version} [https://github.com/Reemote/ree-reecu-sec/releases/download/v1.15.0/sec_ts-v1.15.0-c180346.jed|https://github.com/Reemote/ree-reecu-sec/releases/download/v1.15.0/sec_ts-v1.15.0-c180346.jed]
        Left DEPB: [{depb_version}|https://github.com/Reemote/depb/releases/tag/R{depb_version}]\n
        Right DEPB [{depb_version}|https://github.com/Reemote/depb/releases/tag/R{depb_version}]\n
        h2. Test cycles\n
        h3. [VSR {vsr_version} Core Cycle [vDrive {vdrive_version}, vREECU {vreecu_version}]|https://vayio.atlassian.net/projects/REE?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/testPlayer/{core_cycle_key}]\n
        h3. [VSR {vsr_version} Conventional[vDrive {vdrive_version}, vREECU {vreecu_version}]|https://vayio.atlassian.net/projects/REE?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/testPlayer/{conventional_cycle_key}]\n
        h3. [VSR {vsr_version} w/o_SD Cycle [vDrive {vdrive_version}, vREECU {vreecu_version}]|https://vayio.atlassian.net/projects/REE?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/testPlayer/{wo_sd_cycle_key}]\n
        h3. [VSR {vsr_version} w_SD Cycle [vDrive {vdrive_version}, vREECU {vreecu_version}]|https://vayio.atlassian.net/projects/REE?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/testPlayer/{w_sd_cycle_key}]\n
        h3. [VSR {vsr_version} [Minimal US release cycle]|https://vayio.atlassian.net/projects/REE?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/testPlayer/{minimal_us_cycle_key}]\n
        h3. [VSR {vsr_version} [US conventional cycle]|https://vayio.atlassian.net/projects/REE?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/testPlayer/{conventional_us_cycle_key}]"""

    create_ett(auth, payload_items)


def create_ett(auth, payload_items):
    url = "https://vayio.atlassian.net/rest/api/2/issue"

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = json.dumps(
        {
            "fields": {
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
        "--vreecu-version",
        type=str,
        help="vREECU version. <major>.<minor>.<patch>",
    )
    parser.add_argument(
        "--depb-version",
        type=str,
        help="vREECU version. <major>.<minor>.<patch>",
    )
    parser.add_argument(
        "--sec-version",
        type=str,
        help="vREECU version. <major>.<minor>.<patch>",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
