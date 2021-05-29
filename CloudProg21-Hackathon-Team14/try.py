import boto3
import os, fnmatch

def detect_labels(photo, bucket):

    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=1) # 10->1

    print('-----')
    print('Detected labels for ' + photo)
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

def ToSQS():

    # Create SQS client
    sqs = boto3.client('sqs')
    queue_url = 'SQS_QUEUE_URL'

    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageAttributes={
            'Title': {
                'DataType': 'String',
                'StringValue': 'The Whistler'
            },
            'Author': {
                'DataType': 'String',
                'StringValue': 'John Grisham'
            },
            'WeeksOn': {
                'DataType': 'Number',
                'StringValue': '6'
            }
        },
        MessageBody=(
            'Information about current NY Times fiction bestseller for '
            'week of 12/11/2016.'
        )
    )

    print(response['MessageId'])

def main():
    
    s3 = boto3.resource('s3')

    for bucket in s3.buckets.all():   
         print(bucket.name)
         bucket_original = bucket.name
         bucket = s3.Bucket(bucket.name)

         for obj in bucket.objects.all():
            if obj.key.endswith("jpg") or obj.key.endswith("png"):
                print(obj.key)
                photo = str(obj.key)
                detect_labels(photo, bucket_original)

    # exit()
    # photo='test5.jpg'
    # detect_labels(photo, bucket)
   
if __name__ == "__main__":
    main()