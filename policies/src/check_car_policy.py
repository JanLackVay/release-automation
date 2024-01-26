import os

import snowflake.connector
import yaml

RELEASE_CONFIG_QUERY = """
WITH ranked_versions AS (
  SELECT
    vay_system_release,
    vdrive_major_version,
    vdrive_minor_version,
    vdrive_patch_version,
    depb_right_version_string,
    vreecu_version,
    ROW_NUMBER() OVER (PARTITION BY vay_system_release
                       ORDER BY vdrive_patch_version ASC) AS row_num
  FROM dwh.core_driving.sessions
  WHERE vay_system_release IS NOT NULL AND depb_right_version_string IS NOT NULL
)
SELECT
  SPLIT_PART(vay_system_release, '-', 2) as vay_system_release,
  concat(vdrive_major_version, '.', vdrive_minor_version, '.', vdrive_patch_version) as vdrive_version,
  vdrive_major_version,
  vdrive_minor_version,
  vdrive_patch_version,
  depb_right_version_string,  
  vreecu_version
FROM ranked_versions
QUALIFY row_num = 1
ORDER BY 
  CAST(SPLIT_PART(vay_system_release, '.', 1) AS INTEGER) DESC,
  CAST(SPLIT_PART(vay_system_release, '.', 2) AS INTEGER) DESC,
  CAST(SPLIT_PART(vay_system_release, '.', 3) AS INTEGER) DESC
LIMIT 3;
"""
VEHICLE_QUERY = """
select
  TO_CHAR(_ingested_at, 'YYYY-MM-DD HH24:MI') AS "Session started UTC"
  , vehicle:name as "name"
  , concat(CAST(vehicle:software_version:sem_ver_tag:major AS INTEGER), '.', CAST(vehicle:software_version:sem_ver_tag:minor AS INTEGER), '.', CAST(vehicle:software_version:sem_ver_tag:patch AS INTEGER)) as "vdrive_version"
  , CAST(vehicle:software_version:sem_ver_tag:major AS INTEGER) as "vdrive_major_version"
  , CAST(vehicle:software_version:sem_ver_tag:minor AS INTEGER) as "vdrive_minor_version"
  , CAST(vehicle:software_version:sem_ver_tag:patch AS INTEGER) as "vdrive_patch_version"
  , concat(vehicle:depb_left_version:major, '.', vehicle:depb_left_version:minor, '.', vehicle:depb_left_version:patch) as "depb_left"
  , concat(vehicle:depb_right_version:major, '.', vehicle:depb_right_version:minor, '.', vehicle:depb_right_version:patch) as "depb_right"
  , concat(vehicle:reecu:mcu_fw_version:major, '.', vehicle:reecu:mcu_fw_version:minor, '.', vehicle:reecu:mcu_fw_version:patch) as "vreecu_version"
from dwh.raw_driving.session_init
where true
  and vehicle:name LIKE any ('ve-0%', 've-us-%')
  and _ingested_at >= CURRENT_DATE() - INTERVAL '30 DAY'
  and concat(vehicle:depb_right_version:major, '.', vehicle:depb_right_version:minor, '.', vehicle:depb_right_version:patch) is NOT NULL
  and concat(vehicle:reecu:mcu_fw_version:major, '.', vehicle:reecu:mcu_fw_version:minor, '.', vehicle:reecu:mcu_fw_version:patch) is NOT NULL
  and concat(vehicle:software_version:sem_ver_tag:major, '.', vehicle:software_version:sem_ver_tag:minor, '.', vehicle:software_version:sem_ver_tag:patch) is NOT NULL
  QUALIFY 
  ROW_NUMBER() OVER (PARTITION BY vehicle:name ORDER BY _ingested_at DESC) = 1
  ORDER BY vehicle:name ASC
LIMIT 50
"""

TELESTATION_QUERY = """
select
  TO_CHAR(_ingested_at, 'YYYY-MM-DD HH24:MI') AS "Session started UTC"
  , telestation:name as "name"
  , concat(CAST(telestation:software_version:sem_ver_tag:major AS INTEGER), '.', CAST(telestation:software_version:sem_ver_tag:minor AS INTEGER), '.', CAST(telestation:software_version:sem_ver_tag:patch AS INTEGER)) as "vdrive_version"
  , cast(telestation:software_version:sem_ver_tag:major as integer) as "vdrive_major_version"
  , cast(telestation:software_version:sem_ver_tag:minor as integer) as "vdrive_minor_version"
  , cast(telestation:software_version:sem_ver_tag:patch as integer) as "vdrive_patch_version"
  , concat(telestation:reecu:mcu_fw_version:major, '.', telestation:reecu:mcu_fw_version:minor, '.', telestation:reecu:mcu_fw_version:patch) as "vreecu_version"
from dwh.raw_driving.session_init
where true
  and telestation:name LIKE any ('ts-ber-0%', 'ts-las-0%', 'ts-gd%', 'ts-ham-0%')
  and _ingested_at >= CURRENT_DATE() - INTERVAL '30 DAY'
  and concat(telestation:reecu:mcu_fw_version:major, '.', telestation:reecu:mcu_fw_version:minor, '.', telestation:reecu:mcu_fw_version:patch) is NOT NULL
  and concat(telestation:software_version:sem_ver_tag:major, '.', telestation:software_version:sem_ver_tag:minor, '.', telestation:software_version:sem_ver_tag:patch) is NOT NULL
  QUALIFY 
  ROW_NUMBER() OVER (PARTITION BY telestation:name ORDER BY _ingested_at DESC) = 1
  ORDER BY vehicle:name ASC
LIMIT 50
"""


def main():
    query_config = yaml.safe_load(open("../config.yaml", "r"))
    fleet_level_ve = yaml.safe_load(open("../fleet_level_ve.yaml", "r"))
    fleet_level_ts = yaml.safe_load(open("../fleet_level_ts.yaml", "r"))

    development_fleet_ve = fleet_level_ve["development"]
    development_fleet_ts = fleet_level_ts["development"]

    con = snowflake.connector.connect(
        user=query_config["user"],
        authenticator=query_config["authenticator"],
        account=query_config["account"],
        warehouse=query_config["warehouse"],
        database=query_config["database"],
        session_parameters={"QUERY_TAG": "Get ODD ID by name"},
    )

    release_configuration = get_release_configurations(con)
    vehicle_configuration = load_vehicle_configuration(con)
    telestation_configuration = load_telestation_configuration(con)

    mismatched_vehicles, matched_vehicles = compare_vehicle_configuration(
        vehicle_configuration, release_configuration, development_fleet_ve
    )

    mismatched_telestations, matched_telestations = compare_telestation_configuration(
        telestation_configuration, release_configuration, development_fleet_ts
    )

    print(
        "*Release Configuration* \n"
        + configuration_string(release_configuration)
        + "\n"
        + "*Mismatched Telestations* \n"
        + misconfiguration_string(mismatched_telestations)
        + "\n"
        + "*Mismatched Vehicles* \n"
        + misconfiguration_string(mismatched_vehicles)
    )

    return (
        "*Release Configuration* \n"
        + configuration_string(release_configuration)
        + "\n"
        + "*Mismatched Telestations* \n"
        + misconfiguration_string(mismatched_telestations)
        + "\n"
        + "*Mismatched Vehicles* \n"
        + misconfiguration_string(mismatched_vehicles)
    )


def get_release_configurations(con):
    release_configs = con.cursor().execute(RELEASE_CONFIG_QUERY).fetchall()
    release_configurations = []
    for row in release_configs:
        release = {}
        release["vay_system_release"] = row[0]
        release["vdrive_version"] = row[1]
        release["vdrive_major_version"] = row[2]
        release["vdrive_minor_version"] = row[3]
        release["vdrive_patch_version"] = row[4]
        release["depb_version"] = row[5]
        release["vreecu_version"] = row[6]
        release_configurations.append(release)
    return release_configurations


def load_vehicle_configuration(con) -> dict:
    vehicle_output = con.cursor().execute(VEHICLE_QUERY).fetchall()
    vehicle_configuration = {}

    for vehicle in vehicle_output:
        vehicle_configuration[vehicle[1].replace('"', "")] = {
            "vdrive_version": vehicle[2],
            "vdrive_major_version": vehicle[3],
            "vdrive_minor_version": vehicle[4],
            "vdrive_patch_version": vehicle[5],
            "depb_left": vehicle[6],
            "depb_right": vehicle[7],
            "vreecu_version": vehicle[8],
        }
    return vehicle_configuration


def load_telestation_configuration(con) -> dict:
    telestation_output = con.cursor().execute(TELESTATION_QUERY).fetchall()
    telestation_configuration = {}
    for telestation in telestation_output:
        telestation_configuration[telestation[1].replace('"', "")] = {
            "vdrive_version": telestation[2],
            "vdrive_major_version": telestation[3],
            "vdrive_minor_version": telestation[4],
            "vdrive_patch_version": telestation[5],
            "vreecu_version": telestation[6],
        }
    return telestation_configuration


def compare_vehicle_configuration(
    vehicle_configuration: dict, release_configurations: dict, list_of_cars: list[str]
) -> tuple[dict, dict]:
    mismatched_vehicles = {}
    matched_vehicles = {}
    for vsr_config in release_configurations:
        matched_vehicles[vsr_config["vay_system_release"]] = []
    for vehicle in vehicle_configuration:
        if vehicle not in list_of_cars:
            match_found = False
            vehicle_params = vehicle_configuration[vehicle]
            for vsr_config in release_configurations:
                if (
                    vehicle_params["vdrive_major_version"]
                    == vsr_config["vdrive_major_version"]
                    and vehicle_params["vdrive_minor_version"]
                    == vsr_config["vdrive_minor_version"]
                    and vehicle_params["vdrive_patch_version"]
                    >= vsr_config["vdrive_patch_version"]
                    and vehicle_params["vreecu_version"] == vsr_config["vreecu_version"]
                    and vehicle_params["depb_right"] == vsr_config["depb_version"]
                ):
                    match_found = True
                    matched_vehicles[vsr_config["vay_system_release"]].append(vehicle)
                    break

            if not match_found:
                mismatched_vehicles[vehicle] = {
                    "vdrive_version": vehicle_params["vdrive_version"],
                    "vreecu_version": vehicle_params["vreecu_version"],
                    "depb_right": vehicle_params["depb_right"],
                }
    return mismatched_vehicles, matched_vehicles


def compare_telestation_configuration(
    telestation_configuration: dict,
    release_configurations: dict,
    list_of_telestations: list[str],
):
    mismatched_telestations = {}
    matched_telestations = {}

    for vsr_config in release_configurations:
        matched_telestations[vsr_config["vay_system_release"]] = []

    for telestation in telestation_configuration:
        if telestation not in list_of_telestations:
            match_found = False
            telestation_params = telestation_configuration[telestation]
            for vsr_config in release_configurations:
                if (
                    telestation_params["vdrive_major_version"]
                    == vsr_config["vdrive_major_version"]
                    and telestation_params["vdrive_minor_version"]
                    == vsr_config["vdrive_minor_version"]
                    and telestation_params["vdrive_patch_version"]
                    >= vsr_config["vdrive_patch_version"]
                    and telestation_params["vreecu_version"]
                    == vsr_config["vreecu_version"]
                ):
                    match_found = True
                    matched_telestations[vsr_config["vay_system_release"]].append(
                        telestation
                    )
                    break

            if not match_found:
                mismatched_telestations[telestation] = {
                    "vdrive_version": telestation_params["vdrive_version"],
                    "vreecu_version": telestation_params["vreecu_version"],
                }
    return mismatched_telestations, matched_telestations


def misconfiguration_string(
    mismatched_configuraiton: dict,
):
    mismatched_vehicles_string = ""

    for host in mismatched_configuraiton:
        mismatched_vehicles_string = mismatched_vehicles_string + host + "\n"
        for key in mismatched_configuraiton[host]:
            if key != list(mismatched_configuraiton[host].keys())[-1]:
                mismatched_vehicles_string = (
                    mismatched_vehicles_string
                    + " "
                    + key
                    + " "
                    + str(mismatched_configuraiton[host][key])
                    + " |"
                )
            else:
                mismatched_vehicles_string = (
                    mismatched_vehicles_string
                    + " "
                    + key
                    + " "
                    + str(mismatched_configuraiton[host][key])
                )
        mismatched_vehicles_string = mismatched_vehicles_string + "\n"

    return mismatched_vehicles_string


def configuration_string(release_configurations):
    config_str = ""
    for release_config in release_configurations:
        config_str += "*" + release_config["vay_system_release"] + "* \n"
        config_str += (
            "vdrive_version" + ": " + str(release_config["vdrive_version"]) + " | "
        )
        config_str += (
            "depb_version" + ": " + str(release_config["depb_version"]) + " | "
        )
        config_str += "vreecu_version" + ": " + str(release_config["vreecu_version"])
        config_str += "\n"
    return config_str


if __name__ == "__main__":
    main()
