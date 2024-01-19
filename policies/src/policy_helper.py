import requests

URL = "http://operations-odd.prod.vay.local:8080/api/v2/odds"
HEADERS = {"Content-Type": "application/json"}


def sendPolicyAPIRequest(odd_id: str, new_policy_ids: str, send_request=True):
    # Configuration variables
    api_params = {
        "odd": {"id": odd_id, "vehicleConfigurationPolicyIds": new_policy_ids},
        "setMask": "odd.vehicleConfigurationPolicyIds",
    }
    return APIRequest(api_params, send_request)


def sendAccessTypeAPIRequest(odd_id: str, new_access_type: str, send_request=True):
    # Configuration variables
    api_params = {
        "odd": {"id": odd_id, "accessType": new_access_type},
        "setMask": "odd.accessType",
    }
    return APIRequest(api_params, send_request)


def sendLifecycleAPIRequest(odd_id: str, new_lifecycle_state: str, send_request=True):
    # Configuration variables
    api_params = {
        "odd": {"id": odd_id, "lifecycleStatus": new_lifecycle_state},
        "setMask": "odd.lifecycleStatus",
    }
    return APIRequest(api_params, send_request)


def APIRequest(api_params: dict[str, dict[str, str]], send_request=True):
    if send_request:
        # Send a REST API request
        try:
            response = requests.request("POST", URL, json=api_params, headers=HEADERS)
            print(response.json())
            return response.json
        except requests.exceptions.RequestException as e:
            print(f"API Request Failed: {e}")
            return e
    else:
        return api_params
