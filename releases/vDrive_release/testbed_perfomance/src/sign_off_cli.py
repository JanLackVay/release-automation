import json
import os
import pathlib
import subprocess
from typing import Dict

import src.retrieve_logs as retrieve_logs
import yaml

jenkins_url = "http://jenkins-ber.reeinfra.net/view/Main%20Testbed%20Queues/"
job_name = "job/release-testbed-validation-gamma"
build_info_url = f"{jenkins_url}{job_name}"


def main():
    credentials = get_credentials()
    last_successful_build = retrieve_logs.get_last_build_information("Successful", credentials, build_info_url)
    console_log = retrieve_logs.get_console_logs(credentials, last_successful_build, build_info_url)
    list_of_builds = get_last_3_succesfull_builds(last_successful_build, credentials, build_info_url)
    metrics_yaml = get_log_yaml(console_log)

    print("")
    print(metrics_yaml)
    #print("")
    #print(get_udp_tcp_results(test_bed_results))
    print(list_of_builds)


def get_credentials() -> json:
    current_dir = os.getcwd()
    with open(pathlib.Path(f"{current_dir}/../credentials/credentials.yaml"), "r") as f:
        credentials = yaml.safe_load(f)

    return credentials


def get_log_yaml(console_log: str):
    lines = console_log.split("\n")

    start_index = next((i for i, line in enumerate(lines) if "Yaml output starts" in line), None)
    end_index = next((i for i, line in enumerate(lines) if "Yaml output ends" in line), None)
    # If the pattern is found, create a new multiline string from that line onwards
    if start_index is not None and end_index is not None:
        filtered_multiline_string = "\n".join(lines[start_index + 1 : end_index])
    else:
        print("Patterns not found in the multiline string.")

    return filtered_multiline_string


def get_last_3_succesfull_builds(last_successful_build: int, credentials: Dict[str, str], build_info_url):
    build_list = []
    build_number = last_successful_build
    last_branch = retrieve_logs.get_session_information(last_successful_build, credentials, build_info_url)["branch"]

    while len(build_list) < 4:
        log_information = retrieve_logs.get_session_information(build_number, credentials, build_info_url)
        branch = log_information["branch"]
        if last_branch != branch:
            break
        if log_information["result"] == "SUCCESS":
            build_list.append({"build": build_number, "session_id": log_information["session_id"], "branch": branch, "time": log_information["time"]})
        build_number -= 1
    return build_list

def collect_metrics(list_of_builds: list, credentials: Dict[str, str], build_info_url):
    all_metrics = []
    for build in list_of_builds:
        console_log = retrieve_logs.get_console_logs(credentials, build['build'], build_info_url)
        metrics_yaml = yaml.safe_load(get_log_yaml(console_log))
        all_metrics.append(metrics_yaml)
    return all_metrics

def get_metrics_average(all_metrics):
    metrics_average = all_metrics[0].copy()

    for key in all_metrics[0].keys():
        for subkey in all_metrics[0]["front camera bitrate_kbits_per_second"].keys():
            key_value = 0
            for metric in all_metrics:
                key_value += metric[key][subkey]['value']
            metrics_average[key][subkey]['status'] = metric[key][subkey]['status']
            metrics_average[key][subkey]['threshold'] = metric[key][subkey]['threshold']
            metrics_average[key][subkey]['value'] = round(key_value / len(all_metrics))
    return metrics_average

def get_session_id(build: int):
    return 0


if __name__ == "__main__":
    main()
