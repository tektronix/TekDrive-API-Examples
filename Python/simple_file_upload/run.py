import argparse
import os
import sys

import requests

# Put your access key here. The access key must have the `drive:api:directory:create` claim
ACCESS_KEY = "YOUR_ACCESS_KEY"
BASE_URL = "https://drive.api.tekcloud.com"


def create_file_record(file_name: str) -> dict:
    """
    Create the file record in TekDrive
    https://initialstate.github.io/oxford/#api-File-CreateFile
    """
    create_file_url = f"{BASE_URL}/file"
    headers = {
        "X-IS-AK": ACCESS_KEY
    }
    body = {
        "name": file_name
    }
    try:
        r = requests.post(create_file_url, json=body, headers=headers)
        r.raise_for_status()
        create_response = r.json()
    except requests.exceptions.HTTPError as err:
        print('Error creating file record')
        raise err

    return create_response


def upload(upload_url: str, file_path: str) -> None:
    """
    Upload file to storage
    """
    with open(file_path, 'r') as data:
        try:
            r = requests.put(
                upload_url,
                data=data,
                headers={"Content-Type": "application/octet-stream"},
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print('Error uploading file')
            raise err


def main(*args, file_path: str, name: str) -> None:
    if not os.path.isfile(file_path):
        print("Input file does not exist")
        sys.exit()

    create_response = create_file_record(name)
    upload(create_response["uploadUrl"], file_path)

    print("File succesfully uploaded")
    print(f"View it here: https://drive.tekcloud.com/#/f/{create_response['file']['id']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="The file to be upload")
    parser.add_argument("--name", help="Filename override", default="test-simple-file-upload")
    args = parser.parse_args()
    main(**args.__dict__)
