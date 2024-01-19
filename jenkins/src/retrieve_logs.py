import subprocess
from typing import Dict

import requests


def get_console_logs(
    credentials: Dict[str, str], last_successful_build: int, build_info_url: str
) -> str:
    console_log = requests.get(
        f"{build_info_url}/{last_successful_build}/consoleFull",
        auth=(credentials["username"], credentials["credentials"]),
    )
    if not console_log.ok:
        print(console_log.reason)

    return console_log.text


def get_last_build_information(
    condition: str, credentials: Dict[str, str], build_info_url: str
) -> int:
    console_log = requests.get(
        f"{build_info_url}/last{condition}Build/buildNumber",
        auth=(credentials["username"], credentials["credentials"]),
    )
    if not console_log.ok:
        print(console_log.reason)

    return int(console_log.text)


def get_session_information(
    build_number: int, credentials: Dict[str, str], build_info_url: str
) -> bool:
    console_log = requests.get(
        f"{build_info_url}/{build_number}/api/json",
        auth=(credentials["username"], credentials["credentials"]),
    )
    result = console_log.json()["result"]
    if result == "ABORTED":
        print("Error: Couldn't retrieve any information.")
        return {"result": None}
    elif console_log.json()["actions"][2] == {}:
        print("Error: Couldn't retrieve any information.")
        return {"result": None}
    else:
        branch = console_log.json()["actions"][2]["parameters"][0]["value"]
        if console_log.json()["description"] != "None":
            session_id = str(console_log.json()["description"]).split("\n")[0]
        time = console_log.json()["timestamp"]
        print(result)
        return {
            "result": result,
            "branch": branch,
            "session_id": session_id,
            "time": time,
        }
