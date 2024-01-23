import argparse
import re

import requests
import yaml


def main(reecu_tag: str, depb_tag: str):
    gh_token = yaml.safe_load(open("credentials.yaml"))["gh_token"]
    repo_owner = "Reemote"
    reecu_repo_name = "ree-reecu"
    reecu_repo_url = f"https://api.github.com/repos/{repo_owner}/{reecu_repo_name}"
    submodule_path = "external/ree-reecu-sec-r5"

    depb_repo_name = "depb"
    depb_repo_url = f"https://api.github.com/repos/{repo_owner}/{depb_repo_name}"

    tags_url_suffix = "git/refs/tags"

    headers = {
        "Accept": "application/vnd.github+json",
        f"Authorization": "Bearer " + gh_token,
        "X-GitHub-Api-Version": "2022-11-28",
    }

    asset_links = {"reecu": {}, "sec": {}, "depb": {}}

    reecu_repo_tag = get_base_repo_tag(
        reecu_repo_url, tags_url_suffix, headers, reecu_tag
    )
    reecu_repo_asset_link = get_assest_link(reecu_repo_url, headers, reecu_repo_tag)

    asset_links["reecu"]["tag"] = reecu_repo_tag
    asset_links["reecu"]["asset_link"] = reecu_repo_asset_link

    submodule_tag, submodule_url = get_submodule_tag(
        reecu_repo_url, submodule_path, reecu_repo_tag, headers
    )
    submodule_asset_link = get_assest_link(
        submodule_url, headers, submodule_tag, host="ve"
    )

    asset_links["sec"]["tag"] = submodule_tag
    asset_links["sec"]["asset_link"] = submodule_asset_link

    depb_repo_tag = get_base_repo_tag(depb_repo_url, tags_url_suffix, headers, depb_tag)
    depb_assets_link = f"https://github.com/Reemote/depb/releases/{depb_repo_tag}"

    asset_links["depb"]["tag"] = depb_repo_tag
    asset_links["depb"]["asset_link"] = depb_assets_link

    print(asset_links)
    return asset_links


def get_base_repo_tag(
    base_repo_tags_url: str,
    tags_url_suffix: str,
    headers: dict[str, str],
    main_repo_tag: str,
):
    response = requests.get(f"{base_repo_tags_url}/{tags_url_suffix}", headers=headers)

    if response.status_code == 200:
        tags = response.json()
        for tag in tags:
            tag_name = tag["ref"].replace("refs/tags/", "")

            if main_repo_tag in tag_name:
                if tag_name.startswith("v"):
                    main_tag = tag_name
                    break
                elif tag_name.startswith("R"):
                    main_tag = tag_name
                    break
                else:
                    main_tag = tag_name
    if not main_tag:
        raise Exception("Could not find tag")
    return main_tag


def get_submodule_tag(
    base_repo_url: str, submodule_path: str, base_repo_tag: str, headers: dict[str, str]
):
    submodule_url = f"{base_repo_url}/contents/{submodule_path}?ref={base_repo_tag}"
    submodule_url = requests.get(submodule_url, headers=headers).json()["git_url"]
    submodule_sha = requests.get(submodule_url, headers=headers).json()["sha"]

    match = re.match(
        r"https://api.github.com/repos/([^/]+)/([^/]+)/git/trees/([^/]+)", submodule_url
    )

    if match:
        owner, repo = match.groups()[0:2]
        submodule_url = f"https://api.github.com/repos/{owner}/{repo}"
    else:
        raise Exception("Could not parse submodule URL")

    # sumbodule_repo_tag = get_base_repo_tag(submodule_url, tags_url_suffix, headers, main_repo_tag)
    response = requests.get(submodule_url + "/git/refs/tags", headers=headers)
    for sha in response.json():
        if sha["object"]["sha"] == submodule_sha:
            submodule_tag = sha["ref"].replace("refs/tags/", "")

    if not submodule_tag:
        raise Exception("Could not find tag")
    return submodule_tag, submodule_url


def get_assest_link(repo_url: str, headers: dict[str, str], tag: str, host: str = None):
    repo_tag_url = f"{repo_url}/releases/tags/{tag}"
    repo_assets_url = requests.get(repo_tag_url, headers=headers).json()["assets_url"]
    if not repo_assets_url:
        raise Exception("Could not find assets URL")

    repo_assets = requests.get(repo_assets_url, headers=headers).json()

    if host:
        for asset in repo_assets:
            if host in asset["name"]:
                repo_asset_link = asset["browser_download_url"]
                break
        if not repo_asset_link:
            raise Exception("Could not find file")
    else:
        repo_asset_link = repo_assets[0]["browser_download_url"]
    return repo_asset_link


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reecu-tag",
        type=str,
        help="<major>.<minor>.<patch> of the vREECU version to be used.",
        required=True,
    ),
    parser.add_argument(
        "--depb-tag",
        type=str,
        help="<major>.<minor>.<patch> of the DEPB version to be used.",
        required=True,
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(**vars(parse_args()))
