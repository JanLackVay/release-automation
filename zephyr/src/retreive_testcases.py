from src.make_zephyr_request import make_request


def get_all_test_cases(url: str, headers_api: dict[str, str]):
    parameters = {"maxResults": 1}
    initial_test_case_information = make_request(
        url, method="GET", headers=headers_api, params=parameters
    )
    number_of_test_cases = initial_test_case_information["total"]

    parameters = {"maxResults": number_of_test_cases}
    return make_request(url, method="GET", headers=headers_api, params=parameters)
