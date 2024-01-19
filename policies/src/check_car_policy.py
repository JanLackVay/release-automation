import os

import snowflake.connector
import yaml

VEHICLE_QUERY = """
    select
    TO_CHAR(_ingested_at, 'YYYY-MM-DD HH24:MI') AS "Session started UTC"
    , vehicle:name as "name"
    , concat(vehicle:depb_left_version:major, '.', vehicle:depb_left_version:minor, '.', vehicle:depb_left_version:patch) as "DEPB left"
    , concat(vehicle:depb_right_version:major, '.', vehicle:depb_right_version:minor, '.', vehicle:depb_right_version:patch) as "DEPB right"
    , concat(vehicle:software_version:sem_ver_tag:major, '.', vehicle:software_version:sem_ver_tag:minor, '.', vehicle:software_version:sem_ver_tag:patch) as "Vehicle vDrive"
    , concat(vehicle:reecu:mcu_fw_version:major, '.', vehicle:reecu:mcu_fw_version:minor, '.', vehicle:reecu:mcu_fw_version:patch) as "Vehicle REECU"
    , concat(vehicle:reecu:sec_fpga_gw_version:major, '.', vehicle:reecu:sec_fpga_gw_version:minor, '.', vehicle:reecu:sec_fpga_gw_version:patch) as "Vehicle SEC"
    from raw_driving.session_init
    where true
    and vehicle:name LIKE any ('ve-0%', 've-us-%')
    and _ingested_at >= CURRENT_DATE() - INTERVAL '30 DAY'
    and concat(vehicle:depb_right_version:major, '.', vehicle:depb_right_version:minor, '.', vehicle:depb_right_version:patch) is NOT NULL
    and concat(vehicle:reecu:mcu_fw_version:major, '.', vehicle:reecu:mcu_fw_version:minor, '.', vehicle:reecu:mcu_fw_version:patch) is NOT NULL
    and concat(vehicle:software_version:sem_ver_tag:major, '.', vehicle:software_version:sem_ver_tag:minor, '.', vehicle:software_version:sem_ver_tag:patch) is NOT NULL
    and concat(vehicle:reecu:sec_fpga_gw_version:major, '.', vehicle:reecu:sec_fpga_gw_version:minor, '.', vehicle:reecu:sec_fpga_gw_version:patch) is NOT NULL
    QUALIFY 
    ROW_NUMBER() OVER (PARTITION BY vehicle:name ORDER BY _ingested_at DESC) = 1
    ORDER BY vehicle:name ASC
    LIMIT 50
    """

TELESTATION_QUERY = """
    select
    TO_CHAR(_ingested_at, 'YYYY-MM-DD HH24:MI') AS "Session started UTC"
    , telestation:name as "name"
    , concat(telestation:software_version:sem_ver_tag:major, '.', telestation:software_version:sem_ver_tag:minor, '.', telestation:software_version:sem_ver_tag:patch) as "Telestation vDrive"
    , concat(telestation:reecu:mcu_fw_version:major, '.', telestation:reecu:mcu_fw_version:minor, '.', telestation:reecu:mcu_fw_version:patch) as "Telestation REECU"
    , concat(telestation:reecu:sec_fpga_gw_version:major, '.', telestation:reecu:sec_fpga_gw_version:minor, '.', telestation:reecu:sec_fpga_gw_version:patch) as "Telestation SEC"
    from raw_driving.session_init
    where true
    and telestation:name LIKE any ('ts-ber-0%', 'ts-las-0%', 'ts-gd%', 'ts-ham-0%')
    and _ingested_at >= CURRENT_DATE() - INTERVAL '30 DAY'
    and concat(telestation:reecu:mcu_fw_version:major, '.', telestation:reecu:mcu_fw_version:minor, '.', telestation:reecu:mcu_fw_version:patch) is NOT NULL
    and concat(telestation:software_version:sem_ver_tag:major, '.', telestation:software_version:sem_ver_tag:minor, '.', telestation:software_version:sem_ver_tag:patch) is NOT NULL
    and concat(telestation:reecu:sec_fpga_gw_version:major, '.', telestation:reecu:sec_fpga_gw_version:minor, '.', telestation:reecu:sec_fpga_gw_version:patch) is NOT NULL
    QUALIFY 
    ROW_NUMBER() OVER (PARTITION BY telestation:name ORDER BY _ingested_at DESC) = 1
    ORDER BY vehicle:name ASC
    LIMIT 50
    """

VSR_KEYS_VEHICLE = ["vdrive", "reecu", "vehicle_sec", "depb"]
VSR_KEYS_TELESTATION = ["vdrive", "reecu", "telestation_sec"]

VEHICLE_KEYS = ["vehicle_vdrive", "vehicle_reecu", "vehicle_sec", "depb_left"]
TELESTATION_KEYS = ["telestation_vdrive", "telestation_reecu", "telestation_sec"]


def main():
    query_config = yaml.safe_load(open("../config.yaml", "r"))
    release_config = yaml.safe_load(open("../expected_config.yaml", "r"))
    fleet_level_ve = yaml.safe_load(open("../fleet_level_ve.yaml", "r"))
    fleet_level_ts = yaml.safe_load(open("../fleet_level_ts.yaml", "r"))

    release_fleet_ve = fleet_level_ve["release_testing"]
    engineering_fleet_ve = fleet_level_ve["staging"] + fleet_level_ve["pre_production"]
    production_fleet_ve = fleet_level_ve["production"]

    all_cars = release_fleet_ve + engineering_fleet_ve + production_fleet_ve

    release_fleet_ts = fleet_level_ts["release_testing"]
    engineering_fleet_ts = fleet_level_ts["staging"] + fleet_level_ts["pre_production"]
    production_fleet_ts = fleet_level_ts["production"]

    all_telestations = release_fleet_ts + engineering_fleet_ts + production_fleet_ts

    con = snowflake.connector.connect(
        user=query_config["user"],
        authenticator=query_config["authenticator"],
        account=query_config["account"],
        warehouse=query_config["warehouse"],
        database=query_config["database"],
        session_parameters={"QUERY_TAG": "Get ODD ID by name"},
    )

    vehicle_output = con.cursor().execute(VEHICLE_QUERY).fetchall()
    telestation_output = con.cursor().execute(TELESTATION_QUERY).fetchall()

    vehicle_configuration = load_vehicle_configuration(vehicle_output)

    telestation_configuration = load_telestation_configuration(telestation_output)

    mismatched_vehicles, matched_vehicles = compare_vehicle_configuration(
        vehicle_configuration, release_config, all_cars
    )

    mismatched_telestations, matched_telestations = compare_telestation_configuration(
        telestation_configuration, release_config, all_telestations
    )

    print(right_configuration_string(matched_telestations, "telestations"))
    print(misconfiguration_string(mismatched_telestations))
    print(right_configuration_string(matched_vehicles, "vehicles"))
    print(misconfiguration_string(mismatched_vehicles))


def load_vehicle_configuration(vehicle_output: list[tuple]) -> dict:
    vehicle_configuration = {}

    for vehicle in vehicle_output:
        vehicle_configuration[vehicle[1].replace('"', "")] = {
            "depb_right": vehicle[2],
            "depb_left": vehicle[3],
            "vehicle_vdrive": vehicle[4],
            "vehicle_reecu": vehicle[5],
            "vehicle_sec": vehicle[6],
            "date": vehicle[0],
        }
    return vehicle_configuration


def load_telestation_configuration(telestation_output: list[tuple]) -> dict:
    telestation_configuration = {}
    for telestation in telestation_output:
        telestation_configuration[telestation[1].replace('"', "")] = {
            "telestation_vdrive": telestation[2],
            "telestation_reecu": telestation[3],
            "telestation_sec": telestation[4],
            "date": telestation[0],
        }
    return telestation_configuration


def compare_vehicle_configuration(
    vehicle_configuration: dict, release_config: dict, list_of_cars: list[str]
) -> tuple[dict, dict]:
    mismatched_vehicles = {}
    matched_vehicles = {}

    for vsr_config in release_config:
        mismatched_vehicles[vsr_config["VSR"]] = []
        matched_vehicles[vsr_config["VSR"]] = []

    for car in list_of_cars:
        match_found = False
        vehicle_params = vehicle_configuration[car]
        for vsr_config in release_config:
            if (
                vehicle_params["vehicle_sec"] == vsr_config["vehicle_sec"]
                and vehicle_params["vehicle_vdrive"] == vsr_config["vdrive"]
                and vehicle_params["vehicle_reecu"] == vsr_config["reecu"]
                and vehicle_params["depb_left"] == vsr_config["depb"]
            ):
                match_found = True
                matched_vehicles[vsr_config["VSR"]].append(car)
                break
        if match_found == False:
            for vsr_config in release_config:
                mismatched_vehicles[vsr_config["VSR"]].append(
                    {
                        "name": car,
                        "params": {
                            vehicle_key: vehicle_params[vehicle_key]
                            for vsr_key, vehicle_key in zip(
                                VSR_KEYS_VEHICLE, VEHICLE_KEYS
                            )
                            if vehicle_params[vehicle_key] != vsr_config[vsr_key]
                        },
                    }
                )
    return mismatched_vehicles, matched_vehicles


def compare_telestation_configuration(
    telestation_configuration: dict,
    release_config: dict,
    list_of_telestations: list[str],
):
    mismatched_telestations = {}
    matched_telestations = {}

    for vsr_config in release_config:
        mismatched_telestations[vsr_config["VSR"]] = []
        matched_telestations[vsr_config["VSR"]] = []

    for telestation in list_of_telestations:
        match_found = False
        telestation_params = telestation_configuration[telestation]
        for vsr_config in release_config:
            if (
                telestation_params["telestation_sec"] == vsr_config["telestation_sec"]
                and telestation_params["telestation_vdrive"] == vsr_config["vdrive"]
                and telestation_params["telestation_reecu"] == vsr_config["reecu"]
            ):
                match_found = True
                matched_telestations[vsr_config["VSR"]].append(telestation)
                break
        if match_found == False:
            for vsr_config in release_config:
                mismatched_telestations[vsr_config["VSR"]].append(
                    {
                        "name": telestation,
                        "params": {
                            telestation_key: telestation_params[telestation_key]
                            for vsr_key, telestation_key in zip(
                                VSR_KEYS_TELESTATION, TELESTATION_KEYS
                            )
                            if telestation_params[telestation_key]
                            != vsr_config[vsr_key]
                        },
                    }
                )
    return mismatched_telestations, matched_telestations


def misconfiguration_string(
    mismatched_configuraiton: dict,
):
    mismatched_vehicles_string = ""
    for release in mismatched_configuraiton:
        mismatched_vehicles_string = (
            mismatched_vehicles_string + "*" + release + "*" + "\n"
        )
        for system in mismatched_configuraiton[release]:
            mismatched_vehicles_string = (
                mismatched_vehicles_string + system["name"] + "\n"
            )
            for key in system["params"]:
                if key != list(system["params"].keys())[-1]:
                    mismatched_vehicles_string = (
                        mismatched_vehicles_string
                        + " "
                        + key
                        + " "
                        + system["params"][key]
                        + " |"
                    )
                else:
                    mismatched_vehicles_string = (
                        mismatched_vehicles_string
                        + " "
                        + key
                        + " "
                        + system["params"][key]
                    )
            mismatched_vehicles_string = mismatched_vehicles_string + "\n"

    return mismatched_vehicles_string


def right_configuration_string(matched_configuraiton: dict, system: str):
    matched_vehicles_string = f"*Correct configured {system}:*\n"
    for release in matched_configuraiton:
        matched_vehicles_string = matched_vehicles_string + "*" + release + "*" + "\n"
        for system in matched_configuraiton[release]:
            if system != list(matched_configuraiton[release])[-1]:
                matched_vehicles_string = matched_vehicles_string + system + " | "
            else:
                matched_vehicles_string = matched_vehicles_string + system
        matched_vehicles_string = matched_vehicles_string + "\n"

    return matched_vehicles_string


if __name__ == "__main__":
    main()
