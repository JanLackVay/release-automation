import argparse
import os
import pathlib
import time

import requests
import src.yaml_loader as yaml_loader

JENKINS_JOB_URL = "http://conveyor.reeinfra.net/view/Release%20Trigger%20Jobs/job/trigger-long-gamma-test-release/api/json"


def main(branch: str, machine: str):
    current_dir = os.getcwd()

    job_configuration = yaml_loader.load_yaml(
        pathlib.Path(f"{current_dir}/config/config.yaml").open().read()
    )["deployment"]

    jenkins_url = job_configuration["jenkins_url"]
    job_name = job_configuration["job_name"]
    parameters = job_configuration["parameters"]

    parameters["VERSION"] = branch
    url = f"{jenkins_url}{job_name}"  # ansible only
    machines = [f"ve-{machine}a", f"ve-{machine}b", f"ts-{machine}a"]

    credentials = yaml_loader.load_yaml(
        pathlib.Path(f"{current_dir}/credentials/credentials.yaml").open().read()
    )
    response = requests.get(
        JENKINS_JOB_URL,
        auth=(credentials["username"], credentials["credentials"]),
    ).json()
    curretn_job_url = response["builds"][0]["url"]
    response = requests.post(
        curretn_job_url + "stop",
        auth=(credentials["username"], credentials["credentials"]),
    )
    print(response.status_code)
    print(response.text)
    print("----" * 10)
    print("Waiting for 10 seconds to stop the current job")
    time.sleep(1)
    for i in range(9, -1, -1):
        if i > 1:
            print(f"Time remaining {i} seconds")
        else:
            print(f"Time remaining {i} second")
        time.sleep(1)
    print("\nDeployment started")

    for machine in machines:
        parameters["MACHINE"] = machine
        response = requests.post(
            url,
            data=parameters,
            auth=(credentials["username"], credentials["credentials"]),
        )
        print(response.status_code)
        print(response.text)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--branch",
        type=str,
        required=True,
        help="Branch which should be deployed.",
    )
    parser.add_argument(
        "--machine",
        type=str,
        default="loki-0001",
        help="Name of TS and VE where the software should be deployed.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
