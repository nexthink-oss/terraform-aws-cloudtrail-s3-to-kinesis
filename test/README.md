## End-to-end tests

End-to-end tests use [Terratest](https://terratest.gruntwork.io/) to spin up real infrastructure, create a S3 bucket, ship a sample CloudTrail log file to it and check that the expected record is produced in Kinesis.

```
# Pre-requisite: ensure you are authenticated against a test/CI AWS account
# $ aws-vault-exec ci-account

$ go test
```

See [`test/fixtures/`](./test/fixtures) for the test scenarios.

Sample output:

```
TestEndToEndFlow 2021-10-11T14:22:25+02:00 retry.go:91: terraform [init -upgrade=false]
TestEndToEndFlow 2021-10-11T14:22:25+02:00 logger.go:66: Running command terraform with args [init -upgrade=false]
TestEndToEndFlow 2021-10-11T14:22:25+02:00 logger.go:66: Initializing modules...
...
TestEndToEndFlow 2021-10-11T14:22:27+02:00 retry.go:91: terraform [apply -input=false -auto-approve -var kinesis-stream-name=cloudtrail-logs-stream -var cloudtrail-bucket-name=sample-cloudtrail-bucket-1633954945 -var region=eu-west-1 -lock=false


...
TestEndToEndFlow 2021-10-11T14:23:52+02:00 logger.go:66: Terraform used the selected providers to generate the following execution
TestEndToEndFlow 2021-10-11T14:23:52+02:00 logger.go:66: plan. Resource actions are indicated with the following symbols:
TestEndToEndFlow 2021-10-11T14:23:52+02:00 logger.go:66:   - destroy

...
PASS
ok  	github.com/nexthink/cloudtrail-to-kinesis	135.814s
```