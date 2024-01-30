from typing import Optional


def filter_test_cases(
    test_case_information: dict,
    desired_labels: list[str],
    with_sd: Optional[bool] = None,
    without_sd: Optional[bool] = None,
):
    test_cases = []
    for test_case in test_case_information["values"]:
        if with_sd is None and without_sd is None:
            if test_case["status"]["id"] == 581121 and any(
                label in test_case["labels"] for label in desired_labels
            ):
                test_cases.append(str(test_case["key"]))
        else:
            if (
                test_case["status"]["id"] == 581121  # ID for approved test cases
                and any(label in test_case["labels"] for label in desired_labels)
                and test_case["customFields"]["With SD Config"] == with_sd
                and test_case["customFields"]["Without SD Config"] == without_sd
            ):
                test_cases.append(str(test_case["key"]))
    return test_cases
