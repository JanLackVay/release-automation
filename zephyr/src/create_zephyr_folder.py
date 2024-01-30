from make_zephyr_request import make_request


def create_vsr_folder(
    headers_api: dict[str, str],
    url: str,
    name: str,
    parent_id: int,
    project_key: str,
    folder_type: str,
):
    payload = {
        "parentId": parent_id,
        "name": name,
        "projectKey": project_key,
        "folderType": folder_type,
    }
    response = make_request(url, method="POST", headers=headers_api, json_data=payload)
    return response["id"]
