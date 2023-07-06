Name: Tyler Ykema
Student #: 1062564
Class: CIS*4010 Assignment 4
Date: Nov. 24, 2021

Below are instructions on how to setup AWS Lambda and GCP Cloud Functions to log and create backups of
files uploaded to a spcific bucket/container.



AWS Lambda Serverless Function Setup/Creation

Bucket Creation:
Step 1: Navigate to s3 console
Step 2: Click 'Create bucket'
Step 3: Enter a bucket name (must be unique)
Step 4: Select region (must be identical to Lambda function)
Step 5: Scroll down and click 'Create bucket'

Lambda function setup:
Step 1: Navigate to AWS Lambda console, click on 'Create function'
Step 2: Choose author from scratch and enter an appropriate name
Step 3: Choose python 3.9, expand 'Change default execution role'
Step 4: Click 'Create function', from code source swap out existing code with submitted code from 'aws_lambda.py'
Step 5: Click deploy in code souce to make code changes
Step 6: Navigate to 'Configuration' tab, then to 'Triggers' 
Step 7: Select 'Add trigger', then 'Select a trigger', search for 's3'
Step 8: Select the bucket you want to log
Step 9: Set event type to 'All object create events', select 'I acknowledge...' and 'Add'
Step 10: Navigate to 'Configuration' then 'Permissions' and click link to the role name
Step 11: From IAM console and in 'Permissions', select 'Add inline policy'
    Alternatively switch to 'json' tab and copy json from submitted file 'lambda_inline_policy.json' and skip below steps
Step 12: From 'Choose a service' select/search 's3', expand dropdown 'Actions'
Step 13: From dropdown 'List' select 'ListAllMyBuckets'
Step 14: From dropdown 'Read' select 'GetObject'
Step 15: From dropdown 'Write' select 'CreateBucket' and 'PutObject'
Step 16: From 'Resouces' dropdown, select 'Add ARN' for 'bucket' then select 'Any' for 'Bucket name'
Step 17: Then select 'Add ARN' for 'object' then select 'Any' for both 'Bucket name' and 'Object name'
Step 18: Select 'Review Policy', enter a policy name, then select 'Create policy'

    Step 11 alt: Using submitted file 'lambda_inline_policy.json' switch to json tab copy over json string

To trigger an event: upload a file to the bucket you selected for the trigger
    From the s3 portal select your bucket, then click upload and choose a file from your device
    If you go back to the portal you will notice a new bucket with same name plus '-backup'

To access logs in CloudWatch: From Lambda console navigate to 'Monitor' tab, then select 'View logs in CloudWatch'
    *note you must upload a file to the bucket before any logs are created



GCP Cloud Functions

Bucket Creation:
Step : Navigate to 'Cloud Storage' by searching for it in the search bar
Step : Click '+ Create Bucket' and enter a globally unique name then click "CREATE"

Function Creation:
Step : Navigate to 'Cloud Functions' by searching for it in the seach bar
Step : Click on '+ Create Function' along second from the top ribbon
Step : Enter a name for the function and select an appropriate region
Step : Set 'Trigger type' to 'Cloud Storage' and 'Event Type' to 'Finalize/Create' from the dropdown
Step : Click on the 'Browse' button inside of 'Bucket' textbox and select appropriate bucket and hit 'Select'
Step : Click on 'Save' then 'Next'
Step : You should now be in the inline editor, set the runtime to 'Python 3.9' and select all and paste submitted 'gcp.py' code
Step : Switch to 'requirements.txt' and copy and paste 'google-cloud-storage' at the bottom of the file (see 'gcp_requirements.txt')
Step : Click on 'Deploy' and wait for deployment to complete

To trigger an event: upload a file to the bucket you selected for the trigger
    From the Cloud Storage portal select you the bucket you created above and click on 'Upload Files'
    If you go back to the portal you will notice a new bucket with same name plus '-backup'

To access logs: from your functions portal, switch to 'LOGS' tab
    *note the logs are strange and often won't show up for many minutes after an event