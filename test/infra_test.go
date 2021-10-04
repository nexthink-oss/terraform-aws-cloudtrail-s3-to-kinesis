package test

import (
	"encoding/json"
	"errors"
	"io"
	"os"
	"path/filepath"
	"strconv"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/kinesis"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/gruntwork-io/terratest/modules/aws"
	"github.com/gruntwork-io/terratest/modules/retry"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

// Helper function to read the contents of a file in the current directory
// and fail the test on error
func ReadTestFile(t *testing.T, relativePath string) io.Reader {
	path, err := os.Getwd()
	if err != nil {
		t.Error(err)
	}

	fullPath := filepath.Join(path, relativePath)
	reader, err := os.Open(fullPath)
	if err != nil {
		t.Error(err)
	}
	return reader
}

// Helper function to read records from a Kinesis stream.
// The Kinesis stream is expected to have only 1 shard
func ReadFromKinesis(t *testing.T, streamName string) []*kinesis.Record {
	sess := session.Must(session.NewSession())
	kinesisClient := kinesis.New(sess)
	stream, err := kinesisClient.DescribeStream(&kinesis.DescribeStreamInput{StreamName: &streamName})
	if err != nil {
		t.Error("Unable to retrieve Kinesis stream properties")
	}
	shards := stream.StreamDescription.Shards
	if len(shards) != 1 {
		t.Error("Expected Kinesis stream to have 1 shard, got " + strconv.Itoa(len(shards)))
	}

	iteratorType := "LATEST"
	iterator, err := kinesisClient.GetShardIterator(&kinesis.GetShardIteratorInput{
		StreamName:        &streamName,
		ShardIteratorType: &iteratorType,
		ShardId:           shards[0].ShardId,
	})
	if err != nil {
		t.Error("Unable to retrieve shard iterator", err)
	}
	if iterator.ShardIterator == nil {
		t.Error("Could not retrieve a shard iterator")
	}

	// Wait until Kinesis records are produced
	result := retry.DoWithRetryInterface(t, "Retrieving Kinesis events", 20, 10*time.Second, func() (interface{}, error) {
		records, err := kinesisClient.GetRecords(&kinesis.GetRecordsInput{
			ShardIterator: iterator.ShardIterator,
		})
		if err != nil {
			return nil, err
		}
		if len(records.Records) == 0 {
			return nil, errors.New("events not received yet")
		}
		return records, nil
	})
	return result.(*kinesis.GetRecordsOutput).Records
}

type EndToEndTest struct {
	t                 *testing.T
	terraformOptions  *terraform.Options
	terraformDir      string
	region            string
	inputFile         string
	bucketName        string
	kinesisStreamName string
	s3Key             string
	assert            func(test *EndToEndTest, records []*kinesis.Record)
}

// Sets up the infrastructure and pre-requisites for the test to run
func (test *EndToEndTest) Prepare() {
	test.terraformOptions = terraform.WithDefaultRetryableErrors(test.t, &terraform.Options{
		TerraformDir: test.terraformDir,
		Vars: map[string]interface{}{
			"kinesis-stream-name":    test.kinesisStreamName,
			"cloudtrail-bucket-name": test.bucketName,
			"region":                 test.region,
		},
	})
	terraform.InitAndApply(test.t, test.terraformOptions)
}

// Performs the end to end test
func (test *EndToEndTest) DoTest() {
	t := test.t

	t.Log("Starting end-to-end test")

	retry.DoWithRetry(t, "Waiting for S3 bucket "+test.bucketName+" to become available", 60, 1*time.Second, func() (string, error) {
		return "", aws.AssertS3BucketExistsE(test.t, test.region, test.bucketName)
	})
	aws.EmptyS3Bucket(t, test.region, test.bucketName)

	t.Log("Uploading sample CloudTrail log file")
	_, err := aws.NewS3Uploader(t, test.region).Upload(&s3manager.UploadInput{
		Bucket: &test.bucketName,
		Key:    &test.s3Key,
		Body:   ReadTestFile(t, test.inputFile),
	})
	if err != nil {
		t.Error(err)
	}

	records := ReadFromKinesis(t, test.kinesisStreamName)
	test.assert(test, records)
}

// Destroys the infrastructure set up in Prepare()
func (test *EndToEndTest) Cleanup() {
	test.t.Log("Cleaning up")
	if test.terraformOptions != nil {
		terraform.Destroy(test.t, test.terraformOptions)
	}
}

func TestEndToEndFlow(t *testing.T) {
	bucketName := "sample-cloudtrail-bucket" + "-" + strconv.FormatInt(time.Now().Unix(), 10)
	test := EndToEndTest{
		t:                 t,
		terraformDir:      "./fixtures/cloudtrail-to-kinesis",
		region:            "eu-west-1",
		bucketName:        bucketName,
		kinesisStreamName: "cloudtrail-logs-stream",
		inputFile:         "fixtures/cloudtrail-to-kinesis/data/cloudtrail-log-file.json.gz",
		s3Key:             "my-trail/AWSLogs/o-0123456789/987654321098/CloudTrail/eu-west-1/2021/10/04/601687128953_CloudTrail_eu-west-1_20211004T1945Z_bnUnMT3KUNZZcmjo.json.gz",
		assert: func(test *EndToEndTest, records []*kinesis.Record) {
			assert := assert.New(t)
			assert.Len(records, 1, "Expected to retrieve a single Kinesis record since all CloudTrail records fit in a single Kinesis record")

			// Parse Kinesis record
			out := struct {
				Records []interface{} `json:"Records"`
			}{}
			err := json.Unmarshal(records[0].Data, &out)
			assert.Nil(err, "Unable to parse Kinesis record as JSON")

			// From the sample CloudTrail log file, a single Kinesis record with 18 CloudTrail entries should have been produced
			assert.Len(out.Records, 18)

			// Ensure outputs are there
			assert.Equal("cloudtrail-logs-stream", terraform.Output(test.t, test.terraformOptions, "kinesis-stream-name"))
			assert.NotNil(terraform.Output(test.t, test.terraformOptions, "kinesis-stream-arn"))
			assert.NotNil(terraform.Output(test.t, test.terraformOptions, "sns-topic-name"))
			assert.NotNil(terraform.Output(test.t, test.terraformOptions, "sns-topic-arn"))
		},
	}

	defer test.Cleanup()
	test.Prepare()
	test.DoTest()
}
