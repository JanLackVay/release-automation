import argparse

import yaml
from atlassian import Jira

JIRA_URL = "https://vayio.atlassian.net"
JIRA_USERNAME = "jan.lack@vay.io"
JIRA_TOKEN = yaml.safe_load(open("credentials.yaml"))["api_token"]

ASSIGNEE = "617969efe79ff6006fae4f89"  # Christoph Siebold


def main(release_number: int):
    jira = Jira(url=JIRA_URL, username=JIRA_USERNAME, password=JIRA_TOKEN)
    fields_epic = dict(
        summary=f"release-{release_number}.0",
        project=dict(key="REE"),
        issuetype=dict(name="Epic"),
    )

    epic = jira.create_issue(fields_epic)
    epic_key = epic["key"]
    update_epic = dict(
        assignee=assigned,
        priority=p0,
        labels=label,
        customfield_10011=epic_name,  # customfield_10011 is epic
        components=component,
    )


def epic_parameters(release_number):
    assigned = {"accountId": ASSIGNEE}
    p0 = {"id": "1"}
    label = [f"vDrive_{release_number}"]
    epic_name = f"release-{release_number}.0"
    component = [{"id": "10181"}]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release-number",
        type=int,
        help="The number of the release.",
        required=True,
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
