import pathlib

import git
import yaml
from atlassian import Confluence

path = pathlib.Path("~/atlassian/config.yaml").expanduser()
ree_drive = pathlib.Path("./ree-drive")
page_title = "– ree-drive Release"
space_key = "ops"


def main():
    with path.open() as file:
        config = yaml.safe_load(file.read())

    confluence = Confluence(
        url=config["url"],
        username=config["user"],
        password=config["oauth"],
        cloud=True,
    )
    create_confluence_page(get_latest_release, confluence)


def get_latest_release():
    repo = git.Repo(ree_drive)
    tags = repo.tags
    release_branches = [tag for tag in tags if tag.name.startswith("v")]
    latest_release = max(
        release_branches, key=lambda t: t.commit.committed_datetime
    ).name
    return latest_release


def create_confluence_page(latest_release, confluence):
    # confluence.create_page(
    #    space="ops",
    #    title=f"{latest_release} {page_title}",
    #    body="This is the body",
    #    parent_id="1231388696",
    #    type="page",
    #    representation="storage",
    #    editor="v2",
    #    full_width=False,
    # )
    page_content = ""

    # Generate the HTML table
    page_content += "<table>"
    page_content += "<tr>"
    page_content += "<th>Configuration</th>"
    page_content += "</tr>"
    page_content += "<tr>"
    page_content += "<td>"
    page_content += "<ul>"
    page_content += "<li>Teledrive station (TS1)</li>"
    page_content += "<li>Safety Controller</li>"
    page_content += "<li>N/A</li>"
    page_content += "<li>Performance Controller</li>"
    page_content += "</ul>"
    page_content += "</td>"
    page_content += "<td>"
    page_content += "<ul>"
    page_content += "<li>OS: Ubuntu 20.04</li>"
    page_content += "</ul>"
    page_content += "</td>"
    page_content += "</tr>"
    page_content += "</table>"

    status = confluence.create_page(
        space=space_key, title=f"Test_jan", body=page_content
    )
    print(status)


if __name__ == "__main__":
    main()
