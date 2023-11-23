import argparse
import os
import pathlib

import requests
import src.yaml_loader as yaml_loader


def main(branch: str, machine: str):
    current_dir = os.getcwd()

    job_configuration = yaml_loader.load_yaml(
        pathlib.Path(f"{current_dir}/config.yaml").open().read()
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

    print(job_configuration)
    print(credentials)

    for machine in machines:
        parameters["MACHINE"] = machine
        r = requests.post(
            url,
            data=parameters,
            auth=(credentials["username"], credentials["credentials"]),
        )
        print(r.status_code)
        print(r.text)


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
