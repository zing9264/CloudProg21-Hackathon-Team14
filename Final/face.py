import os
import io
import json
import boto3
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import logging
import urllib
import urllib.parse

SQS_URL = "https://sqs.us-east-1.amazonaws.com/662802416147/N"
def send_sqs_message(sqs_queue_url, msg_body):
    sqs_client = boto3.client('sqs')
    msg = sqs_client.send_message(QueueUrl=sqs_queue_url, MessageBody=json.dumps(msg_body)) 

BUCKET = "image-final"
KEY_SOURCE = "ITZY(P).jpg"
KEY_TARGET = "IITZYYY.jpg"

# Tutorial https://gist.github.com/alexcasalboni/0f21a1889f09760f8981b643326730ff

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

source_face, matches = compare_faces(BUCKET, KEY_SOURCE, BUCKET, KEY_TARGET)

# print("source Face ({Confidence}%)".format(**source_face))
print("Source Face:", KEY_SOURCE)
print("---")



c =0
mess = {}
for match in matches:
    c+=1
    print("Number ", c, "similar face:")
    print("Target Face", KEY_TARGET)
    print("Similarity : {}%".format(match['Similarity']))
    mess.update({c: match['Similarity']})
    print("---")

print(mess)

'''
output:

(cloud) D:\Cloud-Programming\CloudProg21-Hackathon-Team14\Final>python face.py
Source Face: ITZY(P).jpg
---
Number  1 similar face:
Target Face IITZYYY.jpg
Similarity : 99.7168197631836%
---
{1: 99.7168197631836}
'''