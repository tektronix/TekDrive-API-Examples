import os
import sys
import glob
import argparse
import subprocess
import pprint
from typing import List


import requests

##################################################################################################
#   This is an example of multipart file uploads to the TekDrive API for educational purposes.   #
##################################################################################################

# Put your access key here. The access key must have the `drive:api:directory:create` claim
ACCESS_KEY = "YOUR_ACCESS_KEY"


class TekDriveClient:
    def __init__(
        self, access_key: str, base_url: str = "https://drive.api.tekcloud.com",
    ):
        self.access_key = access_key
        self.base_url = base_url

    def create_file(self, name: str, num_chunks: int) -> dict:
        """
        Docs: https://initialstate.github.io/oxford/#api-File-CreateFile
        """
        create_file_url = f"{self.base_url}/file"
        headers = {"X-IS-AK": self.access_key}
        body = {
            "name": name,
            "numChunks": num_chunks,
        }
        try:
            r = requests.post(create_file_url, json=body, headers=headers)
            r.raise_for_status()
            create_response = r.json()
        except requests.exceptions.HTTPError as err:
            raise err

        return create_response

    def upload_file_part(self, upload_url: str, data) -> str:
        """
        Upload file part/chunk to storage using the information from the create_file response
        """
        try:
            r = requests.put(
                upload_url,
                data=data,
                headers={"Content-Type": "application/octet-stream"},
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise err

        return r.headers["etag"]

    def complete_multipart_upload(
        self, upload_id: str, complete_upload_url: str, parts: List[str]
    ) -> None:
        """
        Docs: https://initialstate.github.io/oxford/#api-File-CompleteMultipartFileUpload
        """
        headers = {"X-IS-AK": self.access_key}
        body = {"uploadId": upload_id, "parts": parts}
        try:
            r = requests.post(complete_upload_url, json=body, headers=headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise err


def upload_part(
    client: TekDriveClient, upload_part_details: dict, part_file: str
) -> str:
    """
    Upload file part to storage
    Returns:
        str: ETag of the uploaded part
    """
    print(f"Upload part number: {upload_part_details['partNumber']} \n")
    with open(part_file, "rb") as file_handle:
        etag = client.upload_file_part(upload_part_details["uploadUrl"], file_handle)
        return etag


def split_file(file: str, file_size_mb: float, split_num: int = 2) -> List[str]:
    """
    Split file into parts using the unix split command
    Returns:
        list: Pathnames of split files to be uploaded
    """
    prefix = os.path.join(os.path.dirname(file), f"{file}_upload_part")
    split_size = int(file_size_mb / split_num)
    split_size = 5 if split_size < 5 else split_size

    if not os.path.exists("%saa" % prefix):
        cl = ["split", "-b%sm" % split_size, file, prefix]
        subprocess.check_call(cl)
    return sorted(glob.glob("%s*" % prefix))


def do_multipart_upload(file: str, file_size_mb: float) -> None:
    """
    Run all of the necessary steps to create a file record, upload file contents
    in multiple parts/chunks, and complete the upload as defined by the TekDrive API.
    """
    # Instantiate simple TekDrive client we will use for API requests
    client = TekDriveClient(access_key=ACCESS_KEY)

    ############################################################
    # 1. Split the file into parts                             #
    ############################################################
    split_parts = split_file(file, file_size_mb)
    num_parts = len(split_parts)

    print(f"File contents will be uploaded in {num_parts} parts \n")

    ############################################################
    # 2. Create the file record to get the upload details.     #
    ############################################################
    file_resp = client.create_file("test-multipart-uploaded-file", num_parts)
    file_record = file_resp["file"]
    file_id = file_record["id"]
    upload_parts = file_resp["uploadParts"]
    complete_upload_url = file_resp["completeUploadUrl"]

    print("New file:")
    pprint.pprint(file_record)
    print("\n")

    ############################################################
    # 2. Upload each part, keeping track of the ETag for each. #
    ############################################################

    # Keep track of ETags for each part
    parts = [dict(partNumber=part["partNumber"], ETag=None) for part in upload_parts]

    for part_number, part_file in enumerate(split_parts):
        part_etag = upload_part(client, upload_parts[part_number], part_file)
        parts[part_number]["ETag"] = part_etag

    print("Parts:")
    pprint.pprint(parts)
    print("\n")

    ############################################################
    # 3. Complete the multipart upload.                        #
    ############################################################
    upload_id = upload_parts[0]["uploadId"]
    print(f"Complete upload id: {upload_id} \n")
    client.complete_multipart_upload(upload_id, complete_upload_url, parts)

    print(f"Successfully completed multipart upload for file: {file_id}")


def main(file: str) -> None:
    file = args.file

    if not os.path.isfile(file):
        print("Input file does not exist")
        sys.exit()

    file_size_mb = os.path.getsize(file) / 1e6
    if file_size_mb <= 5:
        print(
            f"Detected file size of {file_size_mb} MB. Use a file larger than 5 MB for multipart uploads."
        )
        sys.exit()
    else:
        do_multipart_upload(file, file_size_mb)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="The file to be upload")
    args = parser.parse_args()
    main(*args.__dict__)