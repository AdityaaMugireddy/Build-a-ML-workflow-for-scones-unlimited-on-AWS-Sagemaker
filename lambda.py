#first function 
import json
import boto3
import base64
{
  "image_data": "",
  "s3_bucket": "sagemaker-us-east-1-706956709130",
  "s3_key": "test/bicycle_s_000059.png",
  "inferences": []
}

s3 = boto3.client('s3')

def lambda_handler(event, context):
   """A function to serialize target data from S3"""
   # Get the s3 address from the Step Function event input
   key = event['s3_key']
   bucket = event['s3_bucket']
    
   # Download the data from s3 to /tmp/image.png
   s3.download_file(bucket, key, '/tmp/image.png')

    
    # We read the data from a file
   with open("/tmp/image.png", "rb") as f:
       image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
   print("Event:", event.keys())
   return {
       'statusCode': 200,
       'body': {
           "image_data": image_data,
           "s3_bucket": bucket,
           "s3_key": key,
           "inferences": []
           
       }
       
   }

# This is the second lambda function: for classifying image data
import os
import io
import boto3
import json
import base64

# grab environment variables
ENDPOINT_NAME = 'image-classification-2023-08-02-03-43-54-465'
runtime= boto3.client('runtime.sagemaker')

def lambda_handler(event, context):

    # Grab the image_data from the event
    # Use this while attaching this lambda into Step Function. 

    image = event['body']['image_data']
    
    image = base64.b64decode(image)
    
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,ContentType='application/x-image',Body=image)
    print("Response:",response)
    
    result = json.loads(response['Body'].read().decode())
    #print("result: ",result)
    
   # We return the data back to the Step Function    
    event["inferences"] = result
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }

# third function for filtering low-confidence inferences
import json


THRESHOLD = 0.85

class ThresholdConfidenceNotMetError(Exception):
    pass

def lambda_handler(event, context):
    
    # Grab the inferences from the event
    body=event['body']
    print(body)
    data = json.loads(body)
    
    inferences = data['inferences']
    print(inferences)
    
    
    # Check if any values in our inferences are above THRESHOLD
    
    if max(inferences) >= THRESHOLD:
        meets_threshold = True
    else:
        meets_threshold = False
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise ThresholdConfidenceNotMetError("THRESHOLD_CONFIDENCE_NOT_MET")
        

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }