#!/usr/bin/env python
import boto3
import datetime
from datetime import datetime as dt
import sys

print(f"Name of the script      : {sys.argv[0]=}")
print(f"Arguments of the script : {sys.argv[1]=}")
print(f"Arguments of the script : {sys.argv[2]=}")

dbName = sys.argv[1]


sts_client_rds = boto3.client('sts')
assumed_role=sts_client_rds.assume_role(
    RoleArn=sys.argv[2], RoleSessionName="AWSCLI")
credentials2 = assumed_role['Credentials']

client_rds = boto3.client('rds', region_name='ap-southeast-1',
    aws_access_key_id=credentials2['AccessKeyId'],
    aws_secret_access_key=credentials2['SecretAccessKey'],
    aws_session_token=credentials2['SessionToken'],
)

datetoday = datetime.datetime.today()
dateStr = datetoday.strftime("%Y%m%d%H%M%S")
snapIdentifier = dbName + '-' + dateStr
response1 = client_rds.create_db_snapshot(
    DBSnapshotIdentifier=snapIdentifier,
    DBInstanceIdentifier=dbName
)
print(response1)
#     snapshot_id = response1["SnapshotId"]
waiter = client_rds.get_waiter('db_snapshot_completed')

try:
    waiter.wait(DBSnapshotIdentifier=snapIdentifier, WaiterConfig={'Delay' : 30, 'MaxAttempts' : 60})
    
except botocore.exceptions.WaiterError as e:
    if "Max attempts exceeded" in e.message:
            print ("Snapshot didn't complete in 600 seconds.")
    else :
        print (e.message)
        
print ("create Snap ", snapIdentifier, " is completed")
sourceFile = open('identifier.txt', 'w')
print(snapIdentifier, file = sourceFile)
sourceFile.close()