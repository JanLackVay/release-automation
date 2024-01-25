import argparse

import yaml

from create_engineering_test_ticket import main as create_engineering_test_ticket
from create_epic import main as create_epic
from create_test_cycles import main as create_test_cycles
from extract_gh_assets import main as extract_gh_assets


def main(
    vsr_version: str,
    vdrive_version: str,
    vreecu_version: str,
    depb_version: str,
    regression: bool == False,
):
    """
    vsr_version = None
    vdrive_version = "56.0.1"
    vreecu_version = "8.3.0"
    depb_version = "2.3.0"
    regression = False

    vsr_version = "2.13.0"
    vdrive_version = "56.0.1"
    vreecu_version = "8.3.0"
    depb_version = "2.3.0"
    regression = False
    """

    cycle_information = {
        "conventional": {"key": "REE-R1100"},
        "core": {"key": "REE-R1101"},
        "with_sd": {"key": "REE-R1102"},
        "without_sd": {"key": "REE-R1103"},
        "minimal_us": {"key": "REE-R1104"},
        "conventional_us": {"key": "REE-R1105"},
    }

    if vsr_version:
        epic_id = create_epic(vsr_version=vsr_version, vdrive_version=vdrive_version)
        print(epic_id)
        cycle_information = create_test_cycles(
            vsr_version=vsr_version,
            vdrive_version=vdrive_version,
            vreecu_version=vreecu_version,
            regression=regression,
        )
        gh_assets = extract_gh_assets(vreecu_version, depb_version)
        print(gh_assets)

        ett = create_engineering_test_ticket(
            vsr_version,
            vdrive_version,
            gh_assets["reecu"],
            gh_assets["depb"],
            gh_assets["sec"],
            cycle_information,
            regression,
            epic_id,
        )
    else:
        epic_id = create_epic(vsr_version=None, vdrive_version=vdrive_version)
        print(epic_id)
        cycle_information = create_test_cycles(
            vsr_version=None,
            vdrive_version=vdrive_version,
            vreecu_version=None,
            regression=None,
        )

        ett = create_engineering_test_ticket(
            vsr_version=None,
            vdrive_version=vdrive_version,
            vreecu_assets=None,
            depb_assets=None,
            sec_ve_assets=None,
            cycle_information=cycle_information,
            regression=False,
            parent_epic_id=epic_id,
        )
    print(ett)


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
    parser.add_argument(
        "--depb-version",
        type=str,
        help="DEPB version. <major>.<minor>.<patch>",
    )
    parser.add_argument(
        "--regression",
        type=lambda x: x.lower() == "true",
        help="If regression test cycle should be created true, else false.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
