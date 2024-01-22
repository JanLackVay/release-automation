import argparse
from typing import List, Optional

import requests
import yaml

URL = "https://api.zephyrscale.smartbear.com/v2"
FOLDER_ID_VSR_TEST_CYCLE = 9263028
FOLDER_ID_VDRIVE_TEST_CYCLE = 9141542


def main(vsr_version: str, vdrive_version: str, vreecu_version):
    api_token = yaml.safe_load(open("credentials.yaml"))["api_token"]
    headers_api = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": api_token,
    }
    test_case_information = get_all_test_cases(
        url=f"{URL}/testcases?", headers_api=headers_api
    )

    if not vsr_version:
        print("Create vDrive test cycle")
        test_cycle_information = create_vdrive_test_cyle(
            headers_api, vdrive_version, test_case_information
        )
    else:
        print("Create VSR test cycle")
        test_cycle_information = create_vsr_test_cycle(
            headers_api,
            vsr_version,
            vdrive_version,
            vreecu_version,
            test_case_information,
        )
    return test_cycle_information


def create_vsr_test_cycle(
    headers_api: dict[str, str],
    vsr_version: str,
    vdrive_version: str,
    vreecu_version: str,
    test_case_information: dict[str, str],
):
    parent_id = create_vsr_folder(
        headers_api,
        url=f"{URL}/folders",
        name=f"VSR {vsr_version}",
        parent_id=FOLDER_ID_VSR_TEST_CYCLE,
    )
    # convetional
    conventional_cycle_key = create_test_cycle_folder(
        headers_api,
        parent_id,
        name=f"VSR {vsr_version} Conventional [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )
    conventional_tests = filter_test_cases(
        test_case_information, desired_labels=["Conventional"]
    )
    assign_testcases_to_testcycle(
        url=f"{URL}/testexecutions",
        headers_api=headers_api,
        testCycleKey=conventional_cycle_key,
        test_cases=conventional_tests,
    )

    # core
    core_cycle_key = create_test_cycle_folder(
        headers_api,
        parent_id,
        name=f"VSR {vsr_version} Core Cycle [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )
    core_tests = filter_test_cases(
        test_case_information,
        desired_labels=["vDrive_sys", "vREECU_sys"],
        w_sd_config=True,
        wo_sd_config=True,
    )
    assign_testcases_to_testcycle(
        url=f"{URL}/testexecutions",
        headers_api=headers_api,
        testCycleKey=core_cycle_key,
        test_cases=core_tests,
    )

    # without sd
    wo_sd_cycle_key = create_test_cycle_folder(
        headers_api,
        parent_id,
        name=f"VSR {vsr_version} w/o_SD Cycle [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )

    wo_sd_tests = filter_test_cases(
        test_case_information,
        desired_labels=["vDrive_sys", "vREECU_sys"],
        w_sd_config=False,
        wo_sd_config=True,
    )
    assign_testcases_to_testcycle(
        url=f"{URL}/testexecutions",
        headers_api=headers_api,
        testCycleKey=wo_sd_cycle_key,
        test_cases=wo_sd_tests,
    )

    # with sd
    w_sd_cycle_key = create_test_cycle_folder(
        headers_api,
        parent_id,
        name=f"VSR {vsr_version} w_SD Cycle [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )

    w_sd_tests = filter_test_cases(
        test_case_information,
        desired_labels=["vDrive_sys", "vREECU_sys"],
        w_sd_config=True,
        wo_sd_config=False,
    )
    assign_testcases_to_testcycle(
        url=f"{URL}/testexecutions",
        headers_api=headers_api,
        testCycleKey=w_sd_cycle_key,
        test_cases=w_sd_tests,
    )

    # us minimal
    minimal_us_cycle_key = create_test_cycle_folder(
        headers_api,
        parent_id,
        name=f"VSR {vsr_version} US Minimal [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )

    us_min_tests = filter_test_cases(
        test_case_information,
        desired_labels=["US_release_O3.3"],
    )
    assign_testcases_to_testcycle(
        url=f"{URL}/testexecutions",
        headers_api=headers_api,
        testCycleKey=minimal_us_cycle_key,
        test_cases=us_min_tests,
    )

    # us conventional
    conventional_us_cycle_key = create_test_cycle_folder(
        headers_api,
        parent_id,
        name=f"VSR {vsr_version} Conventional US [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )
    us_conv_tests = filter_test_cases(
        test_case_information, desired_labels=["Conventional"]
    )
    assign_testcases_to_testcycle(
        url=f"{URL}/testexecutions",
        headers_api=headers_api,
        testCycleKey=conventional_us_cycle_key,
        test_cases=us_conv_tests,
    )

    return {
        "conventional_cycle_key": conventional_cycle_key,
        "core_cycle_key": core_cycle_key,
        "wo_sd_cycle_key": wo_sd_cycle_key,
        "w_sd_cycle_key": w_sd_cycle_key,
        "minimal_us_cycle_key": minimal_us_cycle_key,
        "conventional_us_cycle_key": conventional_us_cycle_key,
    }


def create_vdrive_test_cyle(
    headers_api: dict[str, str],
    vdrive_version: str,
    test_case_information: dict[str, str],
):
    vdrive_tests = filter_test_cases(test_case_information, desired_labels=["vDrive"])
    print(vdrive_tests)

    vdrive_cycle_key = create_test_cycle_folder(
        headers_api,
        parent_id=FOLDER_ID_VDRIVE_TEST_CYCLE,
        name=f"vDrive release-{vdrive_version}",
    )

    assign_testcases_to_testcycle(
        url=f"{URL}/testexecutions",
        headers_api=headers_api,
        testCycleKey=vdrive_cycle_key,
        test_cases=vdrive_tests,
    )
    return {"vdrive_cycle_key": vdrive_cycle_key}


def get_all_test_cases(url: str, headers_api: dict[str, str]):
    parameters = {"maxResults": 1}
    initial_test_case_information = requests.get(
        url, headers=headers_api, params=parameters
    ).json()
    number_of_test_cases = initial_test_case_information["total"]

    parameters = {"maxResults": number_of_test_cases}
    return requests.get(url, headers=headers_api, params=parameters).json()


def create_vsr_folder(headers_api: dict[str, str], url: str, name: str, parent_id: int):
    payload = {
        "parentId": parent_id,
        "name": name,
        "projectKey": "REE",
        "folderType": "TEST_CYCLE",
    }
    headers = headers_api
    response = requests.post(url, json=payload, headers=headers)
    return response.json()["id"]


def create_test_cycle_folder(headers_api: dict[str, str], parent_id: int, name: str):
    url = f"{URL}/testcycles"
    payload = {
        "projectKey": "REE",
        "folderId": parent_id,
        "name": name,
        "projectKey": "REE",
    }
    response = requests.post(url, json=payload, headers=headers_api)
    print(name + " " + response.text)
    return response.json()["key"]


def filter_test_cases(
    test_case_information: dict,
    desired_labels: list[str],
    w_sd_config: Optional[bool] = None,
    wo_sd_config: Optional[bool] = None,
):
    test_cases = []
    for test_case in test_case_information["values"]:
        if w_sd_config is None and wo_sd_config is None:
            if test_case["status"]["id"] == 581121 and any(
                label in test_case["labels"] for label in desired_labels
            ):
                test_cases.append(str(test_case["key"]))
        else:
            if (
                test_case["status"]["id"] == 581121  # ID for approved test cases
                and any(label in test_case["labels"] for label in desired_labels)
                and test_case["customFields"]["With SD Config"] == w_sd_config
                and test_case["customFields"]["Without SD Config"] == wo_sd_config
            ):
                test_cases.append(str(test_case["key"]))
    return test_cases


def assign_testcases_to_testcycle(url, headers_api, testCycleKey, test_cases):
    url = "https://api.zephyrscale.smartbear.com/v2/testexecutions"
    parameters = {
        "projectKey": "REE",
        "testCycleKey": testCycleKey,
        "statusName": "Not Executed",
    }

    for test_case in test_cases:
        parameters["testCaseKey"] = test_case
        initial_test_case_information = requests.post(
            url, headers=headers_api, json=parameters
        ).json()


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
    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
