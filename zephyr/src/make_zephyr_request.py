import time

import requests


def make_request(url, method="GET", headers=None, json_data=None, params=None):
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data)

        response.raise_for_status()

        if response.status_code == 403:
            handle_rate_limit(response)

        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Request error occurred: {err}")


def handle_rate_limit(response):
    remaining_requests = int(response.headers.get("X-RateLimit-Remaining", 0))
    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))

    if remaining_requests == 0:
        # Sleep until the rate limit resets
        sleep_time = max(0, reset_time - int(time.time()))
        print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)
        # Make the request again
        return True
    else:
        return False
