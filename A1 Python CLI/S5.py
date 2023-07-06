#Name: Tyler Ykema
#Student #: 1062564
#Date: 3/10/2021
#CIS*4010 Assignment 1

import sys
import os
import boto3
from botocore.exceptions import ClientError
import logging
from urllib.parse import urlparse
import configparser
from pathlib import Path
from datetime import datetime, timezone

print("Welcome to the AWS S3 Storage Shell (S5)")

config = configparser.ConfigParser()
config.read('s5-s3conf')

#profile = 'tykema'
profile = 'tykema@uoguelph.ca'

ACCESS_KEY_ID = config.get(profile, 'aws_access_key_id')
ACCESS_SECRET_KEY = config.get(profile, 'aws_secret_access_key')

try:
    s3 = boto3.resource("s3", aws_access_key_id = ACCESS_KEY_ID, aws_secret_access_key = ACCESS_SECRET_KEY)
    client = boto3.client("s3", aws_access_key_id = ACCESS_KEY_ID, aws_secret_access_key = ACCESS_SECRET_KEY)
    sts = boto3.client('sts', aws_access_key_id = ACCESS_KEY_ID, aws_secret_access_key = ACCESS_SECRET_KEY)
    sts.get_caller_identity()
except:
    print("You could not be connected to your S3 storage\nPlease review procedures for authenticating your account on AWS S3")
    sys.exit()

print("You are now connected to your S3 storage")

def get_bucket_name(inVar): #gets bucket name from args
    bucket_name = ''
    if (':' in inVar):
        bucket_name = inVar.split(":")[0]
    elif ('/' not in inVar):
        bucket_name = inVar
    return bucket_name

def get_dir_name(inVar): #gets directory name from args
    dir_name = ''
    if (':' in inVar):
        dir_name = inVar.split(":")[1]
    elif('/' in inVar):
        dir_name = inVar
    return dir_name

def create_folder(bucket_name, dir_name):
    dir_name = dir_name.replace('\\', '/')

    if dir_name.endswith('/'): #remove ending /, added on later
        dir_name = dir_name[:-1]

    if not dir_name: #bucket_name parsing is not very good at distinguishing between bucket vs folders without ':' present
        dir_name = bucket_name

    if not check_bucket_exists(bucket_name) and not bucket_name: #if given bucket doesn't exist, set to relative bucket
        #dir_name = bucket_name
        bucket_name = curr_bucket

    if not check_object_exists(bucket_name, curr_dir + dir_name): #check if relative object exists, if true make directory name relative
        dir_name = curr_dir + dir_name

    if not check_object_exists(bucket_name, dir_name): #check if folder already exists, if false create folder
        try:
            client.put_object(Bucket = bucket_name, Key = (dir_name + '/'))
        except:
            print("Error creating directory\nUsage:\n\tcreate_folder <bucket name>:<full pathname for the folder>\n\tcreate_folder <full or relative pathname for the folder>")
            return 0
    else:
        print("Folder already exists")
        return 0
    return 1

def print_objects(client, bucket_name, dir_name): #print info about given object/folder
    count = 0
    fail = False

    try:
        response = client.list_objects(Bucket=bucket_name, Prefix=dir_name)
        for content in response.get('Contents', []):
            print(content.get('Key'))
            count += 1
    except:
        print("An error occured please try again")
        fail = True

    if count == 0 and not fail:
        print("Bucket/folder is empty. Nothing to see here")

    return count

def get_object_info(bucket_name, dir_name): #print longer info about object/folder
    print("Bucket name : Path : File name : Size in bytes : Date modiefied")
    try:
        bucket = client.list_objects(Bucket=bucket_name, Prefix=dir_name)
        for content in bucket.get('Contents', []):
            key = os.path.basename(content.get('Key'))
            path = content.get('Key').replace(key, '')
            print(bucket.get('Name') + " : " + path + " : " + os.path.basename(content.get('Key')) + " : " + str(content.get('Size')) + " byte(s) : " + str(content.get('LastModified')))
    except:
        print("Error retrieving data")
    return

def get_bucket_size(bucket_name): #get size of bucket in bytes
    bucket = client.list_objects(Bucket=bucket_name)
    bucket_size = 0
    for content in bucket.get('Contents', []):
        bucket_size += content.get('Size')
    return bucket_size

def print_bucket_info(): #print info about all buckets
    bucket = client.list_buckets()
    print ("Bucket name : Creation date : Size in bytes, Number of objects")
    for content in bucket.get('Buckets', []):
        bucket_name = content.get('Name')
        print(bucket_name + ' : ' + str(content.get('CreationDate')) + ' : ' + str(get_bucket_size(bucket_name)) + ' byte(s) : ' + str(is_bucket_empty(bucket_name, '')) + " objects")
        #print(content.get('Name') + ' ' + str(content.get('CreationDate')) + ' ' + str(content.get('Owner')))
    return

def is_bucket_empty(bucket_name, dir_name): #check if bucket has objects in it
    count = 0
    try:
        response = client.list_objects(Bucket=bucket_name, Prefix=dir_name)
        for content in response.get('Contents', []):
            count += 1
    except:
        print()

    return count

def check_bucket_exists(bucket_name): #check if given bucket_name is a bucket
    for bucket in s3.buckets.all():
        if bucket.name == bucket_name:
            return True
    return False

def check_object_exists(bucket_name, dir_name): #check if object exists in bucket
    if check_bucket_exists(bucket_name):
        result = client.list_objects(Bucket=bucket_name, Prefix=dir_name)
        if 'Contents' in result:
            return True
    return False

def validate_back(inStr): #checks to see if all strings in string array are '..'
    for i in inStr:
        if i == '':
            continue
        elif i != '..':
            return False
    return True

def count_back_amount(inStr): #counts how many '..' there is in string array
    count = 0
    for i in inStr:
        if i == '..':
            count+=1
    return count


curr_bucket = ''
curr_dir = ''

local_dir = os.getcwd()

while(True):
    inVar = input("S5:"+curr_bucket+'/'+curr_dir+">")
    split_amount = 1

    #logic to split arguments by x amount based on functions
    if inVar[:7] == 'lc_copy':
        split_amount = 2
    elif inVar[:7] == 'cl_copy':
        split_amount = 2
    elif inVar[:13] == 'create_bucket':
        split_amount = 10
    elif inVar[:13] == 'create_folder':
        split_amount = 1
    elif inVar[:9] == 'ch_folder':
        split_amount = 1
    elif inVar[:3] == 'cwf':
        split_amount = 0
    elif inVar[:4] == 'list' and inVar[5:7] == '-l':
        split_amount = 2
    elif inVar == 'list' and len(inVar) == 4:
        split_amount = 0
    elif inVar[:4] == 'list':
        split_amount = 1
    elif inVar[:5] == 'ccopy':
        split_amount = 2
    elif inVar[:7] == 'cdelete':
        split_amount = 1
    elif inVar[:13] == 'delete_bucket':
        split_amount = 1

    inSplit = inVar.split(" ", split_amount)
    #print(inSplit)

    if ((inVar == "exit") or (inVar == "quit") or (inVar == "q")): #exit case logic
        print("Thanks for using S5. See you soon!")
        sys.exit()

    elif(inSplit[0] == 'lc_copy'): #lc_copy function
        if len(inSplit) != 3: #check for proper amount of arguments
            print("Usage:/>lc_copy <full or relative pathname of local file> <bucket name>:<full pathname of S3 object>")
            continue

        bucket_name = get_bucket_name(inSplit[2])
        dir_name = get_dir_name(inSplit[2])
        file_name = os.path.basename(inSplit[1])

        if not check_bucket_exists(bucket_name): #if no bucket name in args set bucket_name to the relative bucket user is in
            if not '/' in bucket_name and not dir_name:
                dir_name = bucket_name
            bucket_name = curr_bucket

        try:
            client.upload_file(inSplit[1], bucket_name, dir_name)
        except:
            print("Error uploading file")

    elif(inSplit[0] == 'cl_copy'): #cl_copy functionality
        if len(inSplit) != 3: #check for proper amount of arguments
            print("Usage:/>\n\tcl_copy <bucket name>:<full pathname of S3 file> <full pathname of the local file>\n\tcl_copy <full or relative pathname of S3 file> <full pathname of the local file>")
            continue

        bucket_name = get_bucket_name(inSplit[1])
        dir_name = get_dir_name(inSplit[1])
        file_name = inSplit[2]

        if not check_bucket_exists(bucket_name): #if no bucket name in args set bucket_name to the relative bucket user is in
            if not '/' in bucket_name and not dir_name:
                dir_name = bucket_name
            bucket_name = curr_bucket

        try:
            client.download_file(bucket_name, dir_name, file_name)
        except:
            print("Could not copy cloud file to your local files. Please try again")


    elif(inSplit[0] == 'create_bucket'): #create_bucket functionality
        if len(inSplit) != 2:
            print("Usage:/>create_bucket <bucket name (no spaces)>")
            continue

        bucket_name = inSplit[1]
        location = {'LocationConstraint': 'us-east-2'}
        try:
            s3.create_bucket(Bucket = bucket_name, CreateBucketConfiguration = location)
        except:
            print("Error creating bucket")

    elif(inSplit[0] == 'create_folder'): #create folder functionality
        if len(inSplit) != 2:
            print("Usage:/>\n\tcreate_folder <bucket name>:<full pathname for the folder>\n\tcreate_folder <full or relative pathname for the folder>")
            continue

        create_folder(get_bucket_name(inSplit[1]), get_dir_name(inSplit[1]))

    elif(inSplit[0] == 'ch_folder' or inSplit[0] == 'cf'): #change folder functionality
        if len(inSplit) != 2:
            print("Usage:/>\n\tch_folder <bucket name>\n\tch_folder <bucket name>:<full pathname of directory>\n\tch_folder <full or relative pathname of directory>")
            continue
        bucket_name = get_bucket_name(inSplit[1])
        dir_name = get_dir_name(inSplit[1])
        curr_dir_split = curr_dir.split('/') #splits directory by /, used for ../.. cases
        index = 0
        for i in curr_dir_split: #removes empty spots caused by ending '/' of folders
            if i == '':
                curr_dir_split.pop(index)
            index += 1

        split_dir = inSplit[1].split("/")

        back = validate_back(split_dir) #validate that array with '..' are valid
        back_amount = count_back_amount(split_dir) #counts how many times to move relative path back from '..' inputs

        if dir_name == '/':
            curr_bucket = ''
            curr_dir = ''
            continue

        if back and back_amount > 0: #moves relative position back
            for i in range(back_amount):
                try:
                    curr_dir_split.pop()
                except:
                    curr_bucket = ''
                    break
            curr_dir = '/'.join(curr_dir_split)
        elif not bucket_name and check_object_exists(curr_bucket, curr_dir + dir_name): #if no bucket given and relative positioned object exists add to current relative position
            curr_dir += dir_name
        elif not bucket_name and check_object_exists(curr_bucket, dir_name): #if no bucket given and given object exists set current directory to given
            curr_dir = dir_name
        elif not dir_name and check_bucket_exists(bucket_name): #if no folder given and bucket exists, set relative bucket
            curr_bucket = bucket_name
            curr_dir = ''
        elif check_object_exists(bucket_name, dir_name): #case for full bucket and path given
            curr_bucket = bucket_name
            curr_dir = dir_name
        else:
            print("Error: directory and/or bucket does not exist. Please try again (include all '/')")

    elif(inSplit[0] == 'cwf'): #current working folder funcitonality
        if len(inSplit) != 1:
            print("Usage:/>cwf")
            continue
        if not curr_bucket: #if user is at root
            print("/")
        else:
            print(curr_bucket + ":" + curr_dir)

    elif(inSplit[0] == 'list'): #list functionality
        bucket_name = ''
        dir_name = ''
        is_l = False #'-l' flag tracker
        arg_len = len(inSplit) #check arg/flag length

        if arg_len == 1: #if no other args, use relative path
            bucket_name = ''
            dir_name = ''
        elif arg_len == 2 and inSplit[1] != '-l': #if no '-l' and path is given
            bucket_name = get_bucket_name(inSplit[1])
            dir_name = get_dir_name(inSplit[1])
        elif arg_len == 2 and inSplit[1] == '-l': #if '-l' and no path given
            bucket_name = curr_bucket
            dir_name = curr_dir
            is_l = True
        elif arg_len == 3 and inSplit[1] == '-l': #if '-l' and path given
            bucket_name = get_bucket_name(inSplit[2])
            dir_name = get_dir_name(inSplit[2])
            is_l = True
        else:
            print("Usage:/>list\n\tlist <bucket name>\n\tlist <bucket name>:<full pathname for directory or file>")
            continue

        if not is_l: #displays short list
            if (not curr_bucket and not bucket_name) or dir_name == '/': #info about buckets
                for bucket in s3.buckets.all():
                    print(bucket.name)
            elif not bucket_name and not dir_name: #full relative path info
                print_objects(client, curr_bucket, curr_dir)
            elif not bucket_name: #relative bucket info
                print_objects(client, curr_bucket, dir_name)
            else: #full given path info
                print_objects(client, bucket_name, dir_name)
        else: #displays long list
            if (not curr_bucket and not bucket_name) or dir_name == '/': #info about buckets
                print_bucket_info()
            elif not bucket_name and not dir_name: #full relative path info
                print_objects(client, curr_bucket, curr_dir)
            elif not bucket_name: #relative bucket info
                get_object_info(curr_bucket, dir_name)
            else: #full given path info
                get_object_info(bucket_name, dir_name)

    elif(inSplit[0] == 'ccopy'): #copy objects funcitonality
        if len(inSplit) != 3:
            print("Usage:/>ccopy <from S3 location of object> <to S3 location>")
            continue

        from_bucket = get_bucket_name(inSplit[1])
        from_dir = get_dir_name(inSplit[1])
        if not check_bucket_exists(from_bucket): #checks if relative and makes changes
            if not '/' in from_bucket and not from_dir:
                from_dir = from_bucket
            from_bucket = curr_bucket

        copy_source = {
            'Bucket': from_bucket,
            'Key': from_dir
        }

        to_bucket_name = get_bucket_name(inSplit[2])
        to_dir_name = get_dir_name(inSplit[2])
        if not check_bucket_exists(to_bucket_name): #checks if relative and makes changes
            if not '/' in to_bucket_name and not to_dir_name:
                to_dir_name = to_bucket_name
            to_bucket_name = curr_bucket

        bucket = s3.Bucket(to_bucket_name) #changes bucket if required

        try:
            bucket.copy(copy_source, to_dir_name)
        except:
            print("Error copying file. Please try again")

    elif(inSplit[0] == 'cdelete'): #delete object functionality
        if len(inSplit) != 2:
            print("Usage:/>cdelete <full or indirect pathname of object>")
            continue
        bucket_name = get_bucket_name(inSplit[1])
        dir_name = get_dir_name(inSplit[1])

        if not check_bucket_exists(bucket_name): #checks if relative and changes path variables
            if not '/' in dir_name and not dir_name:
                dir_name = bucket_name
            bucket_name = curr_bucket

        if curr_dir and curr_bucket:
            dir_name = curr_dir + dir_name

        if check_bucket_exists(bucket_name) and dir_name == 'All()': #option to delete all contents of bucket, primarily for ease of testing delete_bucket
            ch = input("Are you sure you want to delete everything in this bucket? (enter: Y or n) ")
            if ch == 'Y':
                try:
                    s3.Bucket(bucket_name).objects.all().delete()
                except:
                    print("Error: could not delete all objects")
            continue

        if not check_object_exists(bucket_name, dir_name): #check the object doesn't exist
            print("Could not perform delete. File does not exist")
            continue

        try:
            s3.Object(bucket_name, dir_name).delete()
        except:
            print("Could not delete object")

    elif(inSplit[0] == 'delete_bucket'): #delete bucket funcitonality
        if len(inSplit) != 2:
            print("Usage:/>delete_bucket <bucket name>")
            continue
        bucket_name = inSplit[1]
        count = is_bucket_empty(bucket_name, '') #check if bucket is empty

        #check if bucket exists
        if not check_bucket_exists(bucket_name): #check if bucket exists
            print("Bucket does not exist. Please enter an existing bucket")
            continue

        if count != 0: #if bucket not empty let user know
            print("Bucket is not empty, there is "+str(count)+" object(s) in the bucket. Empty bucket and try again")
            continue

        if bucket_name == curr_bucket: #reset back to root if current bucket is deleted
            print("Cannot delete bucket you are currently in")
            continue

        try:
            client.delete_bucket(Bucket=bucket_name)
        except:
            print("Error in deleting bucket:\n\tMake sure you are the owner of the bucket\n\tMake sure the bucket is empty")

    elif inSplit[0] == 'cd':
        os.chdir(inSplit[1])

    else:
        os.system(inVar)
