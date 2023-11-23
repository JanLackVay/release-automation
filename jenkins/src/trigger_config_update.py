import argparse
import json
import os
import pathlib

import requests
import src.yaml_loader as yaml_loader


def main(branch: str):
    current_dir = os.getcwd()

    job_configuration = yaml_loader.load_yaml(
        pathlib.Path(f"{current_dir}/config/config.yaml").open().read()
    )["long_test_config"]

    jenkins_url = job_configuration["jenkins_url"]
    job_name = job_configuration["job_name"]
    jsonfile = json.load(open("test.json"))
    jsonfile["properties"]["hudson-model-ParametersDefinitionProperty"][
        "parameterDefinitions"
    ][1][
        "defaultValue"
    ] = branch  # replace the single value
    data = {"json": str(jsonfile)}

    url = f"{jenkins_url}{job_name}"

    credentials = yaml_loader.load_yaml(
        pathlib.Path(f"{current_dir}/credentials/credentials.yaml").open().read()
    )
    print(url)
    r = requests.post(
        url,
        data=data,  # the data you send is a single field which contains all of the json data.
        auth=(credentials["username"], credentials["credentials"]),
    )
    print(r.request.body)
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
    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
