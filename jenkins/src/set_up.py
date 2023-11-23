from typing import Dict

import yaml


def main():
    username = get_user_input('Enter Jenkins username: ')
    credentials = get_user_input('Enter Jenkins token: ')
    credentials_dummy = load_yaml('credentials/credentials_dummy.yaml')
    credentials_dummy['username'] = username
    credentials_dummy['credentials'] = credentials
    write_yaml(credentials_dummy, 'credentials/credentials.yaml')
    print("Updated YAML data:")
    print(yaml.dump(credentials_dummy))

# Function to interactively get user input
def get_user_input(prompt):
    return input(prompt)

def load_yaml(file: str):
    with open(file, 'r') as file:
        data = yaml.safe_load(file)
    return data

def write_yaml(data: Dict[str,str], file: str):
    with open(file, 'w') as file:
        yaml.dump(data, file)

if __name__ == "__main__":
    main()
