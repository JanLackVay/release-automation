import requests
from requests.auth import HTTPBasicAuth

# Jenkins server URL and API endpoint
jenkins_url = 'http://jenkins-ber.reeinfra.net/view/Main%20Testbed%20Queues'
api_endpoint = '/job/release-testbed-validation-gamma/api/json'

# Jenkins API authentication credentials
username = 'jan.lack'
password = '11e8c72db5e66a36df2c15790a0b491fed'

# Number of successful builds to retrieve
num_builds = 3

# Function to fetch successful build numbers
def get_successful_build_numbers(url, auth):
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        data = response.json()
        builds = [build['number'] for build in data['builds'] if build['result'] == 'SUCCESS'][:num_builds]
        return builds
    else:
        print(f"Failed to fetch build numbers. Status code: {response.status_code}")
        return []

# Function to get build console logs
def get_build_logs(build_number, url, auth):
    build_url = f"{url}/job/{build_number}/consoleText"
    response = requests.get(build_url, auth=auth)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch build log for build {build_number}. Status code: {response.status_code}")
        return None

if __name__ == "__main__":
    auth = HTTPBasicAuth(username, password)
    build_numbers = get_successful_build_numbers(jenkins_url + api_endpoint, auth)
    
    for build_number in build_numbers:
        build_log = get_build_logs(build_number, jenkins_url, auth)
        if build_log is not None:
            print(f"Build {build_number} Log:")
            print(build_log)
            print("\n")
