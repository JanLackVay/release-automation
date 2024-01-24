import argparse
import time
from typing import List, Optional

import requests
import yaml

URL = "https://api.zephyrscale.smartbear.com/v2"
PROJECTKEY = "REE"
TEST_EXECTION_STATUS = "Not Executed"
FOLDER_ID_VSR_TEST_CYCLE = 9263028
FOLDER_ID_VDRIVE_TEST_CYCLE = 9141542


def main(vsr_version: str, vdrive_version: str, vreecu_version, regression: bool):
    api_token = yaml.safe_load(open("credentials.yaml"))["api_token"]
    headers_api = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": api_token,
    }

    test_case_url = get_zephyr_url(URL, "testcases")
    test_execution_url = get_zephyr_url(URL, "testexecutions")
    test_folder_url = get_zephyr_url(URL, "folders")

    test_case_information = get_all_test_cases(test_case_url, headers_api)

    if not vsr_version:
        print("Create vDrive test cycle")
        test_cycle_information = create_vdrive_test_cyle(
            headers_api, vdrive_version, test_case_information, test_execution_url
        )
    else:
        print("Create VSR test cycle")
        test_cycle_information = create_vsr_test_cycle(
            headers_api,
            vsr_version,
            vdrive_version,
            vreecu_version,
            test_case_information,
            test_execution_url,
            test_folder_url,
            regression,
        )
    return test_cycle_information


def get_zephyr_url(url: str, application: str):
    return f"{url}/{application}"


def make_request(url, method="GET", headers=None, json_data=None, params=None):
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data)

        response.raise_for_status()

        if response.status_code == 403:
            handle_rate_limit(response)

        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Request error occurred: {err}")


def handle_rate_limit(response):
    remaining_requests = int(response.headers.get("X-RateLimit-Remaining", 0))
    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))

    if remaining_requests == 0:
        # Sleep until the rate limit resets
        sleep_time = max(0, reset_time - int(time.time()))
        print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)
        # Make the request again
        return True
    else:
        return False


def create_vsr_test_cycle(
    headers_api: dict[str, str],
    vsr_version: str,
    vdrive_version: str,
    vreecu_version: str,
    test_case_information: dict[str, str],
    test_execution_url: str,
    test_folder_url: str,
    regression: bool,
):
    parent_id = create_vsr_folder(
        headers_api,
        url=test_folder_url,
        name=f"VSR {vsr_version}",
        parent_id=FOLDER_ID_VSR_TEST_CYCLE,
    )

    cycle_types = [
        "conventional",
        "core",
        "with_sd",
        "without_sd",
        "minimal_us",
        "conventional_us",
    ]

    cycle_information = {}
    cycle_information["core"] = {"with_sd": True, "without_sd": True}
    cycle_information["with_sd"] = {"with_sd": True, "without_sd": False}
    cycle_information["without_sd"] = {"with_sd": False, "without_sd": True}
    cycle_information["conventional"] = {"with_sd": None, "without_sd": None}
    cycle_information["minimal_us"] = {"with_sd": None, "without_sd": None}
    cycle_information["conventional_us"] = {"with_sd": None, "without_sd": None}

    if regression:
        print("Create regression test cycle")
        cycle_types.append("regression")
        cycle_information["regression"] = {"with_sd": None, "without_sd": None}

    for cycle_type in cycle_types:
        cycle_information[cycle_type] = {
            "name": f"VSR {vsr_version} {cycle_type.capitalize()} Cycle [vDrive {vdrive_version}, vREECU {vreecu_version}]",
        }
        if "conventional" in cycle_type:
            cycle_information[cycle_type]["labels"] = ["Conventional"]
        elif "regression" in cycle_type:
            cycle_information[cycle_type]["labels"] = ["Regression"]
        else:
            cycle_information[cycle_type]["labels"] = ["vDrive_sys", "vREECU_sys"]

        cycle_information[cycle_type]["key"] = create_test_cycle_folder(
            headers_api,
            parent_id,
            name=cycle_information[cycle_type]["name"],
        )
        cycle_information[cycle_type]["test_cases"] = filter_test_cases(
            test_case_information,
            desired_labels=cycle_information[cycle_type]["labels"],
            with_sd=cycle_information[cycle_type]["with_sd"],
            without_sd=cycle_information[cycle_type]["without_sd"],
        )
        assign_testcases_to_testcycle(
            url=test_execution_url,
            headers_api=headers_api,
            testCycleKey=cycle_information[cycle_type]["key"],
            test_cases=cycle_information[cycle_type]["test_cases"],
        )

    return cycle_information


def create_vdrive_test_cyle(
    headers_api: dict[str, str],
    vdrive_version: str,
    test_case_information: dict[str, str],
    test_execution_url: str,
):
    vdrive_tests = filter_test_cases(test_case_information, desired_labels=["vDrive"])

    vdrive_cycle_key = create_test_cycle_folder(
        headers_api,
        parent_id=FOLDER_ID_VDRIVE_TEST_CYCLE,
        name=f"vDrive release-{vdrive_version}",
    )
    assign_testcases_to_testcycle(
        url=test_execution_url,
        headers_api=headers_api,
        testCycleKey=vdrive_cycle_key,
        test_cases=vdrive_tests,
    )
    return {"vdrive": {"key": vdrive_cycle_key}}


def get_all_test_cases(url: str, headers_api: dict[str, str]):
    parameters = {"maxResults": 1}
    initial_test_case_information = make_request(
        url, method="GET", headers=headers_api, params=parameters
    )
    number_of_test_cases = initial_test_case_information["total"]

    parameters = {"maxResults": number_of_test_cases}
    return make_request(url, method="GET", headers=headers_api, params=parameters)


def create_vsr_folder(headers_api: dict[str, str], url: str, name: str, parent_id: int):
    payload = {
        "parentId": parent_id,
        "name": name,
        "projectKey": "REE",
        "folderType": "TEST_CYCLE",
    }
    response = make_request(url, method="POST", headers=headers_api, json_data=payload)
    return response["id"]


def create_test_cycle_folder(headers_api: dict[str, str], parent_id: int, name: str):
    url = f"{URL}/testcycles"
    payload = {
        "projectKey": "REE",
        "folderId": parent_id,
        "name": name,
        "projectKey": "REE",
    }
    response = make_request(url, method="POST", headers=headers_api, json_data=payload)
    print(name, response)
    return response["key"]


def filter_test_cases(
    test_case_information: dict,
    desired_labels: list[str],
    with_sd: Optional[bool] = None,
    without_sd: Optional[bool] = None,
):
    test_cases = []
    for test_case in test_case_information["values"]:
        if with_sd is None and without_sd is None:
            if test_case["status"]["id"] == 581121 and any(
                label in test_case["labels"] for label in desired_labels
            ):
                test_cases.append(str(test_case["key"]))
        else:
            if (
                test_case["status"]["id"] == 581121  # ID for approved test cases
                and any(label in test_case["labels"] for label in desired_labels)
                and test_case["customFields"]["With SD Config"] == with_sd
                and test_case["customFields"]["Without SD Config"] == without_sd
            ):
                test_cases.append(str(test_case["key"]))
    return test_cases


def assign_testcases_to_testcycle(url, headers_api, testCycleKey, test_cases):
    payload = {
        "projectKey": PROJECTKEY,
        "testCycleKey": testCycleKey,
        "statusName": TEST_EXECTION_STATUS,
    }

    for test_case in test_cases:
        payload["testCaseKey"] = test_case
        make_request(url, method="POST", headers=headers_api, json_data=payload)


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
        "--regression",
        type=lambda x: x.lower() == "true",
        required=True,
        help="If regression test cycle should be created true, else false.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
