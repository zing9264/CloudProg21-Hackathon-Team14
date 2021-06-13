import os
import json
import boto3
import logging
import urllib
import urllib.parse

SQS_URL = "https://sqs.us-east-1.amazonaws.com/662802416147/N" # 我先把結果暫存在SQS裡面
def send_sqs_message(sqs_queue_url, msg_body):
    sqs_client = boto3.client('sqs')
    msg = sqs_client.send_message(QueueUrl=sqs_queue_url, MessageBody=json.dumps(msg_body)) 
    return msg

# Tutorial https://gist.github.com/alexcasalboni/0f21a1889f09760f8981b643326730ff 比較圖片

def compare_faces(bucket, key, bucket_target, key_target, threshold=80, region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    response = rekognition.compare_faces(SourceImage={
                                        "S3Object": {
                                        "Bucket": bucket,
                                        "Name": key,
                                        }
                                        },
                                        TargetImage={
                                        "S3Object": {
                                        "Bucket": bucket_target,
                                        "Name": key_target,
                                        }
                                        },
                                        SimilarityThreshold=threshold,
    )
    return response['SourceImageFace'], response['FaceMatches']


def lambda_handler(event, context):

    # Get the object from the event and show its content type
    BUCKET = event['Records'][0]['s3']['bucket']['name'] 
    KEY_SOURCE = "ITZY(P).jpg" # Replace: box主人照片(S3)
    KEY_TARGET = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8') 
    source_face, matches = compare_faces(BUCKET, KEY_SOURCE, BUCKET, KEY_TARGET) 
    print("Source Face:", KEY_SOURCE)
    print("---")

    c =0
    mess = {}
    for match in matches: # 印出資訊
        c+=1
        print("Number ", c, "similar face:")
        print("Target Face", KEY_TARGET)
        print("Similarity : {}%".format(match['Similarity']))
        mess.update({c: match['Similarity']})
        print("---")
    
    send_sqs_message(SQS_URL, mess)