# TekDrive Go Examples

## Simple File Upload
This is an example of a simple, single file upload using an access key.

1. Add your access key to the top of the `app.go` script. This access key will need the `drive:api:directory:create` claim.

2. Run the example
```
cd simple_file_upload
go run app.go -file=/path/to/local/file.txt -name=optional_filename_override.txt
```
