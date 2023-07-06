#Name: Tyler Ykema
#Student #: 1062564
#Date: Nov. 24, 2021
#CIS*4010 Assignment 4

import json
import urllib.parse 
import boto3

s3 = boto3.client('s3')
s3res = boto3.resource('s3')

def lambda_handler(event, context):
    print(json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    region = {'LocationConstraint': event['Records'][0]["awsRegion"]}
    c_time = {'LocationConstraint': event['Records'][0]["eventTime"]}["LocationConstraint"]

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        source = {
            'Bucket': bucket,
            'Key': key
        }
        log_bucket = bucket + "-backup"
        upload_bucket = s3res.Bucket(log_bucket)
        try:
            s3.create_bucket(Bucket = log_bucket, CreateBucketConfiguration = region)
            print(log_bucket + " has been created... uploading log file")
        except:
            print(log_bucket + " already exists... uploading log file")
            
        try:
            upload_bucket.copy(source, key)
            #s3.put_object(Body=json.dumps(event, indent=2, sort_keys=True), Bucket=log_bucket, Key=str(c_time) + "_log.txt")
            print("Successfully uploaded backup and created log file: " + c_time + "_log.txt to bucket: " + log_bucket)
        except:
            print("Error creating logfile in bucket: " + log_bucket)
            
        return
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

