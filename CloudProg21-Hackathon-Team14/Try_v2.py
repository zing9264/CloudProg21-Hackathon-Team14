import json
import urllib.parse
import boto3

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


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    
    try:
        response = detect_labels(key, bucket)
        print(response)
        return response
        
    
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
