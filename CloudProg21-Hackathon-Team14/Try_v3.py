import json
import urllib.parse
import boto3
import logging
import os

"""
AWS rekognition 
- detect_labels 搬過來用
- 新增變數c 去算總人數
"""
s3 = boto3.client('s3')
def detect_labels(key, bucket):
    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':key}}, MaxLabels=1) # 10->1
    print('-----')
    print('Detected labels for ' + key)
    print()
    for label in response['Labels']:
        c =0
        print ("Label: " + label['Name'])
        for instance in label['Instances']:
            c+=1
            # print ("  Bounding box")
            # print ("    Top: " + str(instance['BoundingBox']['Top']))
            # print ("    Left: " + str(instance['BoundingBox']['Left']))
            # print ("    Width: " +  str(instance['BoundingBox']['Width']))
            # print ("    Height: " +  str(instance['BoundingBox']['Height']))
            # print ("  Confidence: " + str(instance['Confidence']))
            # print()
        print("Number of Person: ", c)

    print('-----')
    return c

# send to SQS https://www.javacodemonk.com/python-send-event-from-aws-lambda-to-aws-sqs-a5f299dc

def send_sqs_message(sqs_queue_url, msg_body):
    sqs_client = boto3.client('sqs')
    sqs_queue_url = 'https://sqs.us-east-1.amazonaws.com/662802416147/Num' # 先自己測試一下SQS
    
    msg = sqs_client.send_message(QueueUrl=sqs_queue_url,
                                      MessageBody=json.dumps(msg_body)) 
    return msg

# 觸發 lambda
def lambda_handler(event, context):

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        response = detect_labels(key, bucket)
        print(response)
        send_sqs_message('https://sqs.us-east-1.amazonaws.com/662802416147/Num', response)
        return response

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e