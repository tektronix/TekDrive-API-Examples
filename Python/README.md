# TekDrive Python Examples


### Multipart File Upload
This is an example of multipart file uploads using an access key.

1. Create virtual environment and install dependencies
```
cd multipart_file_upload
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

2. Add your access key to the top of the `run.py` script. This access key will need the `drive:api:directory:create` claim.

3. Run the example
```
python3 run.py /path/to/some/local/file.txt
```