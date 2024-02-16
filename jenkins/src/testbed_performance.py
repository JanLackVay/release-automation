import json
import os
import pathlib
import subprocess
from typing import Dict

import yaml

import src.retrieve_logs as retrieve_logs
import src.yaml_loader as yaml_loader

jenkins_url = "http://jenkins-ber.reeinfra.net/view/Main%20Testbed%20Queues/"
job_name = "job/release-testbed-validation-gamma"
build_info_url = f"{jenkins_url}{job_name}"


def main():
    current_dir = os.getcwd()
    credentials = yaml_loader.load_yaml(pathlib.Path(f"{current_dir}/credentials/credentials.yaml").open().read())
    last_successful_build = retrieve_logs.get_last_build_information("Successful", credentials, build_info_url)

    console_log = retrieve_logs.get_console_logs(credentials, last_successful_build, build_info_url)
    list_of_builds = get_last_3_succesfull_builds(last_successful_build, credentials, build_info_url)

    all_metrics = collect_metrics(list_of_builds, credentials, build_info_url)
    metrics_average = get_metrics_average(all_metrics)

    front_camera_packets = "front camera packets per second_packets_per_second"

    list_of_keys_camera_bitrate = [
        "front camera bitrate_kbits_per_second",
        "left camera bitrate_kbits_per_second",
        "right camera bitrate_kbits_per_second",
        "back camera bitrate_kbits_per_second",
    ]

    list_of_keys_camera_new_unit = [
        "front camera Mbit/s",
        "left camera Mbit/s",
        "right camera Mbit/s",
        "back camera Mbit/s",
    ]

    list_of_keys_udp_tcp_bitrate = [
        "ROS UDP_kbits_per_second",
        "ROS TCP_kbits_per_second",
        "UDP TS-VE_kbits_per_second",
        "UDP VE-TS_kbits_per_second",
        "TCP TS-VE_kbits_per_second",
        "TCP VE-TS_kbits_per_second",
    ]

    list_of_keys_udp_tcp_new_unit = [
        "ROS UDP Mbit/s",
        "ROS TCP Mbit/s",
        "UDP TS-VE Mbit/s",
        "UDP VE-TS Mbit/s",
        "TCP TS-VE Mbit/s",
        "TCP VE-TS Mbit/s",
    ]
    print(
        "Average of following builds:",
        [build["build"] for build in list_of_builds],
        "on Branch:",
        list_of_builds[0]["branch"],
    )
    print(
        "front camera packets/s",
        "\t\t",
        round(metrics_average[front_camera_packets]["minimum"]["value"]),
        round(metrics_average[front_camera_packets]["median"]["value"]),
        round(metrics_average[front_camera_packets]["max"]["value"]),
    )

    for key in zip(list_of_keys_camera_bitrate, list_of_keys_camera_new_unit):
        if len(key[1]) < 16:
            tab = "\t\t\t"
        else:
            tab = "\t\t"
        print(
            key[1],
            tab,
            round(metrics_average[key[0]]["minimum"]["value"] / 1000, 2),
            round(metrics_average[key[0]]["median"]["value"] / 1000, 2),
            round(metrics_average[key[0]]["max"]["value"] / 1000, 2),
        )
    print("----------------------------------------")
    print("UDP/TCP Bitrate")
    for key in zip(list_of_keys_udp_tcp_bitrate, list_of_keys_udp_tcp_new_unit):
        if len(key[1]) < 16:
            tab = "\t\t\t"
        else:
            tab = "\t\t"

        print(
            key[1],
            tab,
            round(metrics_average[key[0]]["minimum"]["value"] / 1000, 2),
            round(metrics_average[key[0]]["median"]["value"] / 1000, 2),
            round(metrics_average[key[0]]["max"]["value"] / 1000, 2),
        )


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

    max_iterations = 10
    iterations = 0

    session_info = retrieve_logs.get_session_information(last_successful_build, credentials, build_info_url)

    if session_info["result"] is not None:
        print(session_info)
        last_branch = session_info["branch"]
    else:
        while iterations < max_iterations:
            last_successful_build -= 1
            iterations += 1
            session_info = retrieve_logs.get_session_information(last_successful_build, credentials, build_info_url)
            if session_info["result"] is not None:
                print(session_info)
                last_branch = session_info["branch"]
                break
    print(last_branch)

    while len(build_list) < 1:
        log_information = retrieve_logs.get_session_information(build_number, credentials, build_info_url)
        print(log_information["result"])
        if log_information["result"] == "SUCCESS":
            branch = log_information["branch"]
            if last_branch != branch:
                break
            build_list.append(
                {
                    "build": build_number,
                    "session_id": log_information["session_id"],
                    "branch": branch,
                    "time": log_information["time"],
                }
            )
        build_number -= 1
    return build_list


def get_all_branch_builds(branch: str, last_successful_build: int, credentials: Dict[str, str], build_info_url):
    build_list = []
    build_number = last_successful_build
    current_branch = retrieve_logs.get_session_information(last_successful_build, credentials, build_info_url)["branch"]

    while True:
        if current_branch == branch:
            latest_build_of_branch = build_number
            break
        build_number -= 1

        if retrieve_logs.get_session_information(build_number, credentials, build_info_url) != "Error: Couldn't retrieve any information.":
            current_branch = retrieve_logs.get_session_information(build_number, credentials, build_info_url)["branch"]

    while True:
        log_information = retrieve_logs.get_session_information(build_number, credentials, build_info_url)
        if log_information == "Error: Couldn't retrieve any information.":
            continue

        current_branch = log_information["branch"]
        if branch != current_branch:
            break

        build_list.append(
            {
                "build": build_number,
                "session_id": log_information["session_id"],
                "branch": branch,
                "time": log_information["time"],
                "status": log_information["result"],
            }
        )
        build_number -= 1
    return build_list


def collect_metrics(list_of_builds: list, credentials: Dict[str, str], build_info_url):
    all_metrics = []
    for build in list_of_builds:
        console_log = retrieve_logs.get_console_logs(credentials, build["build"], build_info_url)
        metrics_yaml = yaml.safe_load(get_log_yaml(console_log))
        all_metrics.append(metrics_yaml)
    return all_metrics


def get_metrics_average(all_metrics):
    metrics_average = all_metrics[0].copy()

    for key in all_metrics[0].keys():
        for subkey in all_metrics[0]["front camera bitrate_kbits_per_second"].keys():
            key_value = 0
            for metric in all_metrics:
                key_value += metric[key][subkey]["value"]
            metrics_average[key][subkey]["status"] = metric[key][subkey]["status"]
            metrics_average[key][subkey]["threshold"] = metric[key][subkey]["threshold"]
            metrics_average[key][subkey]["value"] = round(key_value / len(all_metrics))
    return metrics_average


if __name__ == "__main__":
    main()
