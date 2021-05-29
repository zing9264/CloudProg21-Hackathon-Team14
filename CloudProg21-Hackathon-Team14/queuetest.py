# for test
import boto3
import json
# # Get the service resource
# sqs = boto3.resource('sqs')
# # Create the queue. This returns an SQS.Queue instance
# queue = sqs.get_queue_by_name(QueueName='test')
# response = queue.send_message(MessageBody='world')

# print(response.get('MessageId'))
# print(response.get('MD5OfMessageBody'))
item = {
    'store': 'KFC',
    'person_max': 20,
    'person_now': 15,
    'contact': ' {"phone":"0800092000", "address":"XX區XX路XX號" } ',
    'normal': '{"A": 240, "B": 199 }',
    'discount': '{"A":199 } ',
    'tag': ['FastFood','Fried']
}
STARTUP_SIGNUP_TABLE = 'Store_Info'
AWS_REGION = 'us-east-1'
dynamodb = boto3.resource(
    'dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(STARTUP_SIGNUP_TABLE)
response = table.put_item(Item=item)
# response = table.delete_item(Key = {'store':'Bar'})

res = table.get_item(Key={'store': 'KFC'})
item = res['Item']
print(item['contact'])
print(type(item['contact']))
print(json.loads(item['contact']))
# print(type(json.loads(item['contact'])))
print(item['tag'])
print(type(item['tag']))
print(item['tag'][0])

# create S3
# S3 = 'nthu-2021-team14-hackathon'
# s3 = boto3.client('s3')
# response = s3.list_buckets()
# isbucketExist=False
# for bucket in response['Buckets']:
#         if bucket["Name"] == S3:
#             isbucketExist=True
# s3_client = boto3.client('s3')
# s3_client.create_bucket(Bucket=S3)
# istableExist= False
# ddb_conn = boto3.client(
#         'dynamodb', region_name=AWS_REGION)
# res = ddb_conn.list_tables()     
# print(res)
# for table in res['TableNames']:
#     print(table)
#     if table == 'test':
#         istableExist=True  

# if not istableExist:
#     ddb_conn.create_table(
#             TableName="test",
#             KeySchema=[{'AttributeName': 'store', 'KeyType': 'HASH'}],
#             AttributeDefinitions=[
#                 {'AttributeName': 'store', 'AttributeType': 'S'}],
#             ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})