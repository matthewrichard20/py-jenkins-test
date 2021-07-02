#!/usr/bin/env python
import boto3
import datetime
from datetime import datetime as dt
import sys
import time

print(f"Name of the script      : {sys.argv[0]=}")
print(f"Arguments of the script : {sys.argv[1]=}")
print(f"Arguments of the script : {sys.argv[2]=}")


# exportTaskIdentifier = sys.argv[1]
#sys.argv[1] - roleArn
#sys.argv[2] - IamRoleArn
#sys.argv[3] - kmsKey

f = open("identifier.txt", "r")

exportTaskIdentifier =f.read()
exportTaskIdentifier = "devops-rds-staging2-20210701184811"

sts_client_rds = boto3.client('sts')
assumed_role=sts_client_rds.assume_role(
    RoleArn=sys.argv[1], RoleSessionName="AWSCLI")
credentials2 = assumed_role['Credentials']

client_rds = boto3.client('rds', region_name='ap-southeast-1',
    aws_access_key_id=credentials2['AccessKeyId'],
    aws_secret_access_key=credentials2['SecretAccessKey'],
    aws_session_token=credentials2['SessionToken'],
)

dbName = exportTaskIdentifier[:-15]
dateStr = exportTaskIdentifier[-14:]
response2 = client_rds.start_export_task(
        ExportTaskIdentifier=(dbName +'-s3-snapshot-' +dateStr),
        SourceArn='arn:aws:rds:ap-southeast-1:475194349913:snapshot:' + exportTaskIdentifier,
        S3BucketName='zx-backup-db-staging',
        IamRoleArn=sys.argv[2],
        KmsKeyId= sys.argv[3],
        S3Prefix=dbName + '/' + dateStr[:8],
    )
complete = 0
while not(complete):

    sts_client_rds = boto3.client('sts')
    assumed_role=sts_client_rds.assume_role(
        RoleArn=sys.argv[1], RoleSessionName="AWSCLI")
    credentials2 = assumed_role['Credentials']

    client_rds = boto3.client('rds', region_name='ap-southeast-1',
        aws_access_key_id=credentials2['AccessKeyId'],
        aws_secret_access_key=credentials2['SecretAccessKey'],
        aws_session_token=credentials2['SessionToken'],
    )

    reply = client_rds.describe_export_tasks()
    found = ""
    for o in reply["ExportTasks"]:
            if o["ExportTaskIdentifier"] == response2['ExportTaskIdentifier'] :
                complete = (o['Status'] == "COMPLETE")
                print(o['Status'] , " ", complete)
    time.sleep(120)

print ("export Snap ", snapIdentifier, " is completed")