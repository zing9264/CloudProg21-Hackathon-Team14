import json
import urllib.parse
import boto3
import urllib.request
import os
import sys
import subprocess

subprocess.call('pip install Pillow -t /tmp/ --no-cache-dir'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
sys.path.insert(1, '/tmp/')
from PIL import Image
import PIL.Image

s3 = boto3.client('s3')

def resize_image(image_path, resized_path):
  with Image.open(image_path) as image:
      image.thumbnail(tuple(x / 2 for x in image.size))
      image.save(resized_path)

def lambda_handler(event, context):
    # TODO implement
    for record in event['Records']:
        try:
        # TODO: write code...
            bucketname = "cloudprog-hw3-109062530-lambda"
            s3 = boto3.client('s3')
            response = s3.list_buckets()
            isbucketExist=False
            # Output the bucket names
            print('Existing buckets:')
            for bucket in response['Buckets']:
                if bucket["Name"] == bucketname:
                    isbucketExist=True
            if isbucketExist==False:
                s3_client = boto3.client('s3')
                s3_client.create_bucket(Bucket=bucketname)
            print(event)
            print("test")
            payload = record["body"]
            print(str(payload))
            url = urllib.parse.urlparse(str(payload))
            print(url)
            filname= url.path.split('/')[-1]
            print("Downloading image from %s" % url.geturl())
            local_filename, headers = urllib.request.urlretrieve(url.geturl())
            print("local_filename:"+local_filename)
            resize_filename ="resize-"+filname
            print(resize_filename)
            resize_image(local_filename,"/tmp/"+resize_filename)
            print("resizefilname:"+resize_filename)
            s3.upload_file("/tmp/"+resize_filename,bucketname ,resize_filename,ExtraArgs={'ACL':'public-read', 'ContentType': 'image/jpeg'})
            return {'statusCode': 200,'body': json.dumps('Hello from Lambda!')}
        except Exception as e:
            print("An error occurred.")
            print(e)
            return {'statusCode': 400,'body': json.dumps('An error occurred.')}
