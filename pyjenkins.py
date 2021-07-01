#!/usr/bin/env python
import boto3
import datetime
from datetime import datetime as dt

#Client for S3
sts_client = boto3.client('sts')
assumed_role=sts_client.assume_role(
    RoleArn="arn:aws:iam::475194349913:role/zebrax-Lead", RoleSessionName="AWSCLI")
credentials = assumed_role['Credentials']

client=boto3.client(
    's3',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
)

sts_client_rds = boto3.client('sts')
assumed_role=sts_client_rds.assume_role(
    RoleArn="arn:aws:iam::475194349913:role/zebrax-Snapshotdb", RoleSessionName="AWSCLI")
credentials2 = assumed_role['Credentials']

client_rds = boto3.client('rds', region_name='ap-southeast-1',
    aws_access_key_id=credentials2['AccessKeyId'],
    aws_secret_access_key=credentials2['SecretAccessKey'],
    aws_session_token=credentials2['SessionToken'],
)

def isNeedSnap (dbname, numofday) :
    delta = datetime.timedelta(numofday)
    sts_client = boto3.client('sts')
    assumed_role=sts_client.assume_role(
    RoleArn="arn:aws:iam::475194349913:role/zebrax-Lead", RoleSessionName="AWSCLI")
    credentials = assumed_role['Credentials']
    client=boto3.client(
        's3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )
    now = datetime.datetime.now()
    objects = client.list_objects(Bucket='zx-backup-db')
    for o in objects["Contents"]:
        tempstr = o["Key"]
        splitstr = tempstr.split("/")
        if (splitstr[0] == dbname) and (len(splitstr[1]) == 8):
#             print("yes",splitstr)
            if dt.strptime(splitstr[1],"%Y%M%d") <= (now-delta) :
                print(dbname, "need backup")
                return 1
            else :
                print(dbname, "does not need backup")
                return 0

def addTag(dbName) :
    objects2=client_rds.describe_db_instances()
#     listDBName = []
    taglist = ''
    for o in objects2["DBInstances"]:
    #     print ( o["TagList"])
        if o["DBInstanceIdentifier"] == dbName :
            return o["TagList"]

def createSnapFull(dbName) :
#     dbName = 'sharedprojects'
    datetoday = datetime.datetime.today()
    dateStr = datetoday.strftime("%Y%m%d%H%M%S")
    snapIdentifier = dbName + '-' + dateStr
    response1 = client_rds.create_db_snapshot(
        DBSnapshotIdentifier=snapIdentifier,
        DBInstanceIdentifier=dbName,
        Tags= addTag(dbName)
    )
    print(response1)
#     snapshot_id = response1["SnapshotId"]
    waiter = client_rds.get_waiter('db_snapshot_completed')
    
    try:
        waiter.wait(DBSnapshotIdentifier=snapIdentifier, WaiterConfig={'Delay' : 30, 'MaxAttempts' : 60})
        response2 = client_rds.start_export_task(
            ExportTaskIdentifier=(dbName +'-s3-snapshot-' +dateStr),
            SourceArn=response1["DBSnapshot"]["DBSnapshotArn"],
            S3BucketName='zx-backup-db-staging',
            IamRoleArn='arn:aws:iam::475194349913:role/s3-rds-export-snapshot-role',
            KmsKeyId= 'arn:aws:kms:ap-southeast-1:475194349913:key/f6ff887a-facc-4d70-9770-5cd84a975ed9',
            S3Prefix=dbName + '/' + dateStr[:8],
        )
    except botocore.exceptions.WaiterError as e:
        if "Max attempts exceeded" in e.message:
                print ("Snapshot didn't complete in 600 seconds.")
        else :
            print (e.message)
            
    return (response1,response2)

def createSnap(dbName,iamRole) :
#     dbName = 'sharedprojects'
    sts_client_rds = boto3.client('sts')
    assumed_role=sts_client_rds.assume_role(
        RoleArn=iamRole, RoleSessionName="AWSCLI")
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


# In[60]:


# response2


# In[61]:


# response1["DBSnapshot"]["DBSnapshotArn"]


# In[62]:


# datetoday = datetime.datetime.today()
# dateStr = datetoday.strftime("%Y%m%d%H%M%S")
# dateStr


# In[63]:


# datetoday.strftime("%Y%m%d%H%M%S")


# In[78]:


def exportSnap(exportTaskIdentifier) :
    dbName = exportTaskIdentifier[:-15]
    dateStr = exportTaskIdentifier[-14:]
    response2 = client_rds.start_export_task(
        ExportTaskIdentifier=(dbName +'-s3-snapshot-' +dateStr),
        SourceArn='arn:aws:rds:ap-southeast-1:475194349913:snapshot:sharedprojects-20210625111128',
        S3BucketName='zx-backup-db-staging',
        IamRoleArn='arn:aws:iam::475194349913:role/zebrax-SnapshotDB-staging',
        KmsKeyId= 'arn:aws:kms:ap-southeast-1:475194349913:key/f6ff887a-facc-4d70-9770-5cd84a975ed9',
        S3Prefix=dbName + '/' + dateStr[:8],
    )
    import time
    complete = 0
    while not(complete):

        reply = client_rds.describe_export_tasks()
        found = ""
        for o in reply["ExportTasks"]:
             if o["ExportTaskIdentifier"] == exportTaskName :
                complete = (o['Status'] == "COMPLETE")
                print(o['Status'] , " ", complete)
        time.sleep(60)

    print ("export Snap ", snapIdentifier, " is completed")


# In[64]:


# test = "devops-rds-staging-20210628161621"
# exportSnap(test)


# In[ ]:





# In[65]:


# response2 = client_rds.start_export_task(
#     ExportTaskIdentifier=(dbName +'-s3-snapshot-' +'20210625111128'),
#     SourceArn='arn:aws:rds:ap-southeast-1:475194349913:snapshot:sharedprojects-20210625111128',
#     S3BucketName='zx-backup-db',
#     IamRoleArn='arn:aws:iam::475194349913:role/s3-rds-export-snapshot-role',
#     KmsKeyId= 'arn:aws:kms:ap-southeast-1:475194349913:key/f6ff887a-facc-4d70-9770-5cd84a975ed9',
#     S3Prefix=dbName + '/' + dateStr[:8],
# #     ExportOnly=[
# #         'database',
# #     ]
# )
# print(response2)


# In[66]:


# dateStr[:8]


# In[67]:



# response2


# In[68]:


# reply = client_rds.describe_export_tasks()

# # reply
# found = ""
# for o in reply["ExportTasks"]:
# #      print(o["ExportTaskIdentifier"])
#      if o["ExportTaskIdentifier"] == "devops-rds-staging-s3-snapshot-20210629145833" :
#         found = o


# In[69]:


# found['Status']


# In[70]:


# import time


# complete = 0
# while not(complete):
    
#     reply = client_rds.describe_export_tasks()
#     found = ""
#     for o in reply["ExportTasks"]:
#          if o["ExportTaskIdentifier"] == "devops-rds-staging-s3-snapshot-20210629145833" :
#             complete = (o['Status'] == "COMPLETE")
#             print(o['Status'] , " ", complete)
#     time.sleep(60)


# In[71]:


def waiterFinishedExport(exportTaskName) :
    import time


    complete = 0
    while not(complete):

        reply = client_rds.describe_export_tasks()
        found = ""
        for o in reply["ExportTasks"]:
             if o["ExportTaskIdentifier"] == exportTaskName :
                complete = (o['Status'] == "COMPLETE")
                print(o['Status'] , " ", complete)
        time.sleep(60)
    return 1


# In[72]:


# sts_client_s3_rds = boto3.client('sts')
# assumed_role3=sts_client_s3_rds.assume_role(
#     RoleArn="arn:aws:iam::475194349913:role/s3-rds-export-snapshot-role", RoleSessionName="AWSCLI")
# credentials3 = assumed_role3['Credentials']

# client_s3_rds = boto3.client('rds', region_name='ap-southeast-1',
#     aws_access_key_id=credentials3['AccessKeyId'],
#     aws_secret_access_key=credentials3['SecretAccessKey'],
#     aws_session_token=credentials3['SessionToken'],
# )


# In[ ]:




