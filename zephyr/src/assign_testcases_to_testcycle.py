import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

from src.make_zephyr_request import make_request


def assign_testcases_to_testcycle(
    url: str,
    headers_api: str,
    test_cycle_key: str,
    test_cases: List[str],
    project_key: str,
    test_execution_status: str,
    max_workers: int = 10,
    delay_between_request: float = 0.1,
):
    payload = {
        "projectKey": project_key,
        "testCycleKey": test_cycle_key,
        "statusName": test_execution_status,
    }

    def make_single_request(test_case):
        payload_copy = payload.copy()
        payload_copy["testCaseKey"] = test_case
        make_request(url, method="POST", headers=headers_api, json_data=payload_copy)
        time.sleep(0.1)

    # Use ThreadPoolExecutor with a specified max_workers limit
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(make_single_request, test_cases)
