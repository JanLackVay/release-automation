import argparse

import requests
import yaml

URL = "https://api.zephyrscale.smartbear.com/v2/"
FOLDER_ID_VSR_TEST_CYCLE = 9263028
FOLDER_ID_VDRIVE_TEST_CYCLE = 9141542


def main(vsr_version: str, vdrive_version: str, vreecu_version):
    api_token = yaml.safe_load(open("credentials.yaml"))["api_token"]
    if not vsr_version:
        print("Create vDrive test cycle")
        create_vdrive_test_cyle(api_token, vdrive_version, vreecu_version)
    else:
        print("Create VSR test cycle")
        create_vsr_test_cycle(api_token, vsr_version, vdrive_version, vreecu_version)


def create_vsr_test_cycle(api_token, vsr_version, vdrive_version, vreecu_version):
    parent_id = create_vsr_folder(
        api_token, name=f"VSR {vsr_version}", parent_id=FOLDER_ID_VSR_TEST_CYCLE
    )
    convetional_id = create_test_cycle_folder(
        api_token,
        parent_id,
        name=f"VSR {vsr_version} Conventional [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )

    core_id = create_test_cycle_folder(
        api_token,
        parent_id,
        name=f"VSR {vsr_version} Core Cycle [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )

    wo_sd_id = create_test_cycle_folder(
        api_token,
        parent_id,
        name=f"VSR {vsr_version} w/o_SD Cycle [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )

    w_sd_id = create_test_cycle_folder(
        api_token,
        parent_id,
        name=f"VSR {vsr_version} w_SD Cycle [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )

    us_min_id = create_test_cycle_folder(
        api_token,
        parent_id,
        name=f"VSR {vsr_version} Minimal US [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )

    us_conv_id = create_test_cycle_folder(
        api_token,
        parent_id,
        name=f"VSR {vsr_version} Conventional US [vDrive {vdrive_version}, vREECU {vreecu_version}]",
    )

    print("conventional id:" + str(convetional_id))
    print("core id:" + str(core_id))
    print("wo_sd id:" + str(wo_sd_id))
    print("w_sd id:" + str(w_sd_id))
    print("us_min id:" + str(us_min_id))
    print("us_conv id:" + str(us_conv_id))


def create_vdrive_test_cyle(api_token, vdrive_version, vreecu_version):
    vdrive_id = create_test_cycle_folder(
        api_token,
        parent_id=FOLDER_ID_VDRIVE_TEST_CYCLE,
        name=f"vDrive release-{vdrive_version}",
    )

    print("vdrive id:" + str(vdrive_id))


def create_vsr_folder(api_token, name, parent_id):
    url = f"{URL}folders/"
    payload = {
        "parentId": parent_id,
        "name": name,
        "projectKey": "REE",
        "folderType": "TEST_CYCLE",
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": api_token,
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()["id"]


def create_test_cycle_folder(api_token, parent_id, name):
    url = f"{URL}testcycles/"
    payload = {
        "projectKey": "REE",
        "folderId": parent_id,
        "name": name,
        "projectKey": "REE",
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": api_token,
    }
    response = requests.post(url, json=payload, headers=headers)
    print(name + " " + response.text)
    return response.json()["id"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--vsr-version",
        type=str,
        help="VSR version.",
    )
    parser.add_argument(
        "--vdrive-version",
        type=str,
        required=True,
        help="vDrive version. If only vDrive test cycle should be created, use just this argument.",
    )
    parser.add_argument(
        "--vreecu-version",
        type=str,
        help="vREECU version.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
