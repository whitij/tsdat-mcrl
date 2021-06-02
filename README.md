# Tsdat AWS Pipeline Template

This project template contains source code and supporting files for running multiple Tsdat pipelines via a single
serverless (i.e., lambda) application that you can deploy with the AWS SAM CLI. It includes the following files and folders:

- lambda_function - Code for the application's Lambda function and Project Dockerfile.  The lambda function can run
multiple pipelines as defined under the pipelines subfolder.  Each pipeline's code is contained in a further 
subfolder (e.g., lambda_function/pipelines/a2e_buoy_ingest).  You will need to create a folder for each pipeline that
you would like to run via this lambda template. The lambda_function/pipelines/runner.py class contains a map of
regular expressions which are used to map file names of a certain pattern to the pipeline and config files
that will be used to process that specific file.  The regular expressions will need to be updated to work with your
input file name patterns.
- data - Sample data to use for running tests local
- tests - Unit tests for the application code. `tests/test_pipeline.py` is used to run unit tests on your local filesystem.
Anyone can run the local filesystem tests.  `tests/test_lambda_function.py` is used to run unit tests against a test
S3 bucket.  You will need an AWS account and permissions to write to the test bucket in order to run the AWS unit tests.
- template.yaml - A template that defines the application's AWS resources that will be created/managed in a single
software stack via AWS Cloud Formation.  This template defines several AWS resources including Lambda functions,
input/output S3 buckets, and event triggers.  You should modify this template to create the appropriate resources 
needed for your AWS environment.
- samconfig.tomal - A config file containing variables specific to the deployment such as input/output bucket names,
stack name, and the logging level to use.

## Prerequisites
Anyone can edit pipeline code in this template, however the following are required in order to deploy your 
pipeline to AWS:

### 1) Create an AWS account.
Necessary for admins who will deploy your application to AWS

### 2) Configure IAM permissions for your acount.
Necessary for admins who will deploy your application to AWS

### 3) Install Docker
Required to build the AWS Lambda image. [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

### 4) Install AWS CLI
Required to deploy the software stack defined in template.yaml

### 5) Install AWS SAM CLI
Required to deploy the software stack defined in template.yaml
The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that
 adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon
 Linux environment that matches Lambda. It can also emulate your application's build environment and API.

[Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

### 6) Install Python & Tsdat
You will need Python for local testing and development - [Python 3 installed](https://www.python.org/downloads/)
You will also need Tsdat:
```bash
pip install tsdat
```

## Building your lambda function 
Use the `sam build` command to build your lambda function for deployment.

```bash
$ sam build
```

The SAM CLI builds a docker image from a Dockerfile, copies the source of your application inside the Docker image,
and then installs dependencies defined in `lambda_function/requirements.txt` 
inside the docker image. The processed template file is saved in the `.aws-sam/build` folder.


## Deploying your lambda function for the first time
To deploy your application for the first time, run the following in your shell:

```bash
sam deploy --guided
```

This will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, 
and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review.
 If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the 
AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. 
To deploy an AWS CloudFormation stack which creates or modified IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. 
If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to 
the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.


## Deploying your lambda function
Once you have used `sam deploy --guided` to update your samconfig.toml file, you can deploy with the `sam deploy` command.

```bash
$ sam deploy
```
This will package and deploy your built application template to AWS.


## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources.
AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application 
resources such as functions, triggers, and APIs. For resources not included in 
[the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md),
you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html)
resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you 
fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the
 terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
$ sam logs -n HelloWorldFunction --stack-name tsdat-sam-test --tail
```

You can find more information and examples about filtering Lambda function logs in the 
[SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Unit tests

Tests are defined in the `tests` folder in this project. 
`tests/test_pipeline.py` is used to run unit tests on your local filesystem.
Anyone can run the local filesystem tests.

`tests/test_lambda_function.py` is used to run unit tests against a test
S3 bucket.  You will need an AWS account and permissions to write to the test bucket in order to run the AWS unit tests.

The `tests/events` folder contains simulated S3 bucket events that are used for running the pipeline tests against
an AWS S3 bucket.  In order to run  `test_lambda_function.py`, you will need to update the events to match your AWS
test data that should be deposited in a bucket for which you have read permissions.  Specifically, you will need to
update the bucket name property and object key property to match your specific test files as shown in the following
snippet from an event.json file.

```json
{
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "4586d195-b484-464c-97f8-027348232818",
        "bucket": {
          "name": "a2e-tsdat-test",
          "ownerIdentity": {
            "principalId": "A21WSIO2BY6RXE"
          },
          "arn": "arn:aws:s3:::a2e-tsdat-test"
        },
        "object": {
          "key": "a2e_buoy_ingest/humboldt/buoy.z05.00.20201201.000000.zip",
          "size": 3679233,
          "eTag": "84703366a2bac7da56749b6cdbe37de1",
          "sequencer": "00606E62D96731561E"
        }
      }
}

```


## Cleanup

To undeploy your lambda function, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name ${STACK_NAME}
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an 
introduction to SAM specification, the SAM CLI, and serverless application concepts.
