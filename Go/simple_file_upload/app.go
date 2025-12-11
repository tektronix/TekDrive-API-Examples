package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"
)

var baseUrl = "https://drive.api.tekcloud.com/"
var accessKey = "YOUR_ACCESS_KEY"

type CreateFileResponse struct {
	File struct {
		ID    string `json:"id"`
		Owner struct {
			ID       string `json:"id"`
			Username string `json:"username"`
		} `json:"owner"`
		Creator struct {
			ID       string `json:"id"`
			Username string `json:"username"`
		} `json:"creator"`
		Name           string      `json:"name"`
		FileType       string      `json:"fileType"`
		CreatedAt      time.Time   `json:"createdAt"`
		UpdatedAt      time.Time   `json:"updatedAt"`
		SharedAt       interface{} `json:"sharedAt"`
		UploadState    string      `json:"uploadState"`
		Bytes          string      `json:"bytes"`
		Type           string      `json:"type"`
		ParentFolderID string      `json:"parentFolderId"`
		Permissions    struct {
			Owner   bool `json:"owner"`
			Creator bool `json:"creator"`
			Public  bool `json:"public"`
			Read    bool `json:"read"`
			Edit    bool `json:"edit"`
		} `json:"permissions"`
	} `json:"file"`
	UploadURL            string `json:"uploadUrl"`
	StorageLimitExceeded bool   `json:"storageLimitExceeded"`
}

type FileMeta struct {
	Name string `json:"name"`
}

func createFile(fileName string) CreateFileResponse {
	client := http.Client{
		Timeout: time.Second * 2,
	}
	
	fileMeta := FileMeta{fileName}
	jsonReq, err := json.Marshal(fileMeta)

	req, err := http.NewRequest(http.MethodPost, baseUrl + "/file", bytes.NewBuffer(jsonReq))
	if err != nil {
		log.Fatal(err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-IS-AK", accessKey)
	
	res, getErr := client.Do(req)
	if getErr != nil {
		log.Fatal(getErr)
	}
	defer res.Body.Close()

	if res.StatusCode > 200 {
		fmt.Println("Create File HTTP Response Status:", res.StatusCode, http.StatusText(res.StatusCode))
		log.Fatal("File record creation failed")
	}

	body, readErr := ioutil.ReadAll(res.Body)
	if readErr != nil {
		log.Fatal(readErr)
	}
	
	fileRecord := CreateFileResponse{}
	jsonErr := json.Unmarshal(body, &fileRecord)
	
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	return fileRecord
}

func uploadFile(uploadUrl string, filePath string) {
	client := http.Client{
		Timeout: time.Second * 2,
	}

	localFile, err := os.Open(filePath)
	if err != nil {
		log.Fatal(err)
	}
	defer localFile.Close()
	req, err := http.NewRequest("PUT", uploadUrl, localFile)
	if err != nil {
		log.Fatal(err)
	}
	
	// If Content-Length is not set the request will be sent with Transfer-Encoding: chunked
	// Chunked transfer encoding is not supported so you must set the http.Request.ContentLength
	info, _ := localFile.Stat()
	req.ContentLength = info.Size()
	req.Header.Set("Content-Type", "application/octet-stream")

	res, err := client.Do(req)
	if err != nil {
		log.Fatal(err)
	}
	defer res.Body.Close()

	if res.StatusCode > 200 {
		fmt.Println("Upload File HTTP Response Status:", res.StatusCode, http.StatusText(res.StatusCode))
		log.Fatal("File upload failed")
	}
}

func main() {
	filePathPtr := flag.String("file", "../README.md", "Path to file to upload")
	fileNamePtr := flag.String("name", "test-go-file", "Filename override")

	flag.Parse()

	fmt.Println("Uploading file", *filePathPtr, "as", *fileNamePtr)

	// create file meta record
	createResp := createFile(*fileNamePtr)

	// upload file contents
	uploadFile(createResp.UploadURL, *filePathPtr)

	log.Println("Successfully uploaded file")
	log.Println("View it here: " + "https://drive.tekcloud.com/#/f/" + createResp.File.ID)
}
