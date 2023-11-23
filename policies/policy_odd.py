import argparse
import pathlib
import time

import snowflake.connector
import yaml

import src.policy_helper as policy_helper


def main(policy_id, action):
    las_vegas_odds = [
        "las-vegas-odd-imperial-ave",
        "las-vegas-odd-ops-validation",
        "las-vegas-odd-commercial-unlv",
        "las-vegas-odd-city-exploration",
    ]
    berlin_odds = [
        "berlin-odd-v1",
        "berlin-odd-route-30kmh",
        "berlin-odd-northpole",
        "berlin-odd-city-exploration",
    ]
    hamburg_odds = [
        "hamburg-odd-v1.2",
        "hamburg-odd-v1.2.1",
        "hamburg-odd-v1.3",
        "hamburg-odd-v0",
    ]
    all_odds = las_vegas_odds + berlin_odds + hamburg_odds

    if action == "remove":
        print("Removing policy...")
    elif action == "add":
        add_policy_to_odds(policy_id, all_odds)
        print("Adding policy...")


def add_policy_to_odds(policy_id: str, odds: list[str]):
    odd_ids = get_ids_for_odds(odds)

    for odd_id in odd_ids:
        response = policy_helper.sendPolicyAPIRequest(odd_id, policy_id, True)
        print(response)
        print("-----------------")
        time.sleep(1.5)


def get_ids_for_odds(odd_names: list[str]) -> list[str]:
    query_config = yaml.safe_load(open("config.yaml", "r"))

    con = snowflake.connector.connect(
        user=query_config["user"],
        authenticator=query_config["authenticator"],
        account=query_config["account"],
        warehouse=query_config["warehouse"],
        database=query_config["database"],
        session_parameters={"QUERY_TAG": "Get ODD ID by name"},
    )

    query = """select odd_id
    from core_routing.odds 
    where odd_name in (%)
    """

    query = query.replace("%", ", ".join(map(lambda x: f"'{x}'", odd_names)))
    odd_ids = [odd[0] for odd in con.cursor().execute(query).fetchall()]
    return odd_ids


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--policy-id",
        type=str,
        help="The ID of the policy you want to work with.",
    )
    parser.add_argument(
        "--action",
        type=str,
        help="The ID of the policy you want to work with.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
