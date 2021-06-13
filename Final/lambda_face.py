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

SQS_URL = "https://sqs.us-east-1.amazonaws.com/662802416147/Num"
def send_sqs_message(sqs_queue_url, msg_body):
    sqs_client = boto3.client('sqs')
    msg = sqs_client.send_message(QueueUrl=sqs_queue_url, MessageBody=json.dumps(msg_body)) 
    return 0

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


def lambda_handler(event, context):

    # Get the object from the event and show its content type
    BUCKET = event['Records'][0]['s3']['bucket']['name'] #"image-final"
    KEY_SOURCE = "ITZY(P).jpg"
    KEY_TARGET = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8') #"TRY.JPG"



    source_face, matches = compare_faces(BUCKET, KEY_SOURCE, BUCKET, KEY_TARGET)

    # print("source Face ({Confidence}%)".format(**source_face))
    print("Source Face:", KEY_SOURCE)
    print("---")

    c =0
    for match in matches:
        c+=1
        print("Number ", c, "similar face:")
        # print("Target Face ({Confidence}%)".format(**match['Face']))
        print("Target Face", KEY_TARGET)
        print("Similarity : {}%".format(match['Similarity']))
        send_sqs_message(SQS_URL, match['Similarity'])

        print("---")








#Tutorial https://github.com/awsdocs/amazon-rekognition-developer-guide/blob/master/doc_source/compare-faces-console.md
'''
def compare_faces(sourceFile, targetFile):

    client=boto3.client('rekognition')
    # imageSource=urllib.urlopen(sourceFile)
    # imageTarget=urllib.urlopen(targetFile)

   
    imageSource=open(sourceFile)
    imageTarget=open(targetFile)

    response=client.compare_faces(SimilarityThreshold=80,
                                  SourceImage={'Bytes': imageSource.read()},
                                  TargetImage={'Bytes': imageTarget.read()})

    
    for faceMatch in response['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']
        similarity = str(faceMatch['Similarity'])
        print('The face at ' +
              str(position['Left']) + ' ' +
              str(position['Top']) +
              ' matches with ' + similarity + '% confidence')
    imageSource.close()
    imageTarget.close()     
    return len(response['FaceMatches'])     

def main():

    s3 = boto3.resource('s3', region_name='us-east-1')
    bucket = s3.Bucket('image-final')

    source_file='https://image-final.s3.amazonaws.com/ITZY(P).jpg'# Ref (目標)
    target_file='https://image-final.s3.amazonaws.com/ITZY(Group).jpg'# Comparison (測的)

    source_file = urllib.request.urlretrieve(source_file, 'source.png')
    img = Image.open('source.png')
    img.show()
    target_file = urllib.request.urlretrieve(target_file, 'target.png')
    
    face_matches=compare_faces(source_file, target_file)
    print("Face matches: " + str(face_matches))

if __name__ == "__main__":
    main()
'''