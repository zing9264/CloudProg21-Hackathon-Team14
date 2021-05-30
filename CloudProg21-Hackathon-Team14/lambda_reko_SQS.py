import os
import json
import boto3
import logging
import urllib.parse

SQS_URL = "https://sqs.us-east-1.amazonaws.com/486184014670/hackathonQueue"
# AWS rekognition: detect_labels 搬過來用 (不用face是因為如果相片中背對的人也可以算到人數)
s3 = boto3.client('s3')
def detect_labels(bucket, key):
    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':key}}) 

    print('---Start---')
    print('Detected labels for ' + key)
    for label in response['Labels']:
        c =0
        print ("Label: " + label['Name'])
        for instance in label['Instances']:
            c+=1
        if label['Name']=="Person":
            print("Number of Person: ", c)
            return c
    print('---END---')
    return 0


# send to SQS Tutorial: https://www.javacodemonk.com/python-send-event-from-aws-lambda-to-aws-sqs-a5f299dc
def send_sqs_message(sqs_queue_url, msg_body):
    sqs_client = boto3.client('sqs')
    msg = sqs_client.send_message(QueueUrl=sqs_queue_url, MessageBody=json.dumps(msg_body)) 
    
    return msg

# 觸發 lambda
def lambda_handler(event, context):
    print(event)
    print('-')
    
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    # try:
    # # response = detect_labels(key, bucket)
    response = detect_labels(bucket, key)
    print(response)
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Store_Info')
    key = key[:-4]
    print(key)
    table.update_item(
            Key={
                'store': key,
            },
            UpdateExpression="set person_now = :pn",
            ExpressionAttributeValues={
                ':pn': response,
            },
            ReturnValues="UPDATED_NEW"
        )
        
    # msg = send_sqs_message(SQS_URL, response) # 改一下要接收的SQS url 且SQS policy 要開
    # print(msg)
