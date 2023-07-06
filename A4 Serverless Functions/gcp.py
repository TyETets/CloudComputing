#Name: Tyler Ykema
#Student #: 1062564
#Date: Nov. 24, 2021
#CIS*4010 Assignment 4

from google.cloud import storage
import json

def create_bak(source_bucket_name, source_blob_name, dest_bucket_name, dest_blob_name):
    storage_client = storage.Client()
    source_bucket = storage_client.get_bucket(source_bucket_name)
    source_blob = source_bucket.blob(source_blob_name)
    dest_bucket = {}
    try:
        dest_bucket = storage_client.get_bucket(dest_bucket_name)
    except:
        dest_bucket = storage_client.create_bucket(dest_bucket_name)

    return source_bucket.copy_blob(source_blob, dest_bucket, dest_blob_name)


def hello_gcs(event, context):
    file = event
    #print(str(file))
    print(f"Processing file: {file['name']}.")
    print(json.dumps(event, indent=2))

    create_bak(file['bucket'], file['name'], file['bucket'] + '-backup', file['name'])