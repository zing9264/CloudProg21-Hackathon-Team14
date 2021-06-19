# for test
import boto3
import json
# # Get the service resource
# sqs = boto3.resource('sqs')
# # Create the queue. This returns an SQS.Queue instance
# queue = sqs.get_queue_by_name(QueueName='test')
# response = queue.send_message(MessageBody='world')

initUserList = {
    'id': 'Uda9eb6ac80916ec7ec3fd2931d708cd1',
    'name': '謝小姐',
    'Box': ['A_box'],
    'address': ['300新竹市東區光復路二段101號資電館'],
    'phone': '0912345678'
}
AWS_REGION = 'us-east-1'
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
ddb_table = dynamodb.Table('Final_userDB')
ddb_table.put_item(Item=initUserList)
# print(response.get('MessageId'))
# print(response.get('MD5OfMessageBody'))
# items = {
#     'store': 'KFC',
#     'person_max': 20,
#     'person_now': 15,
#     'contact': ' {"phone":"0800092000", "address":"XX區XX路XX號" } ',
#     'normal': '{"A": 240, "B": 199 }',
#     'discount': '{"A":199 } ',
#     'tag': ['FastFood','Fried']
# }
# def dict_to_2Darray(dict_data):
#     array_2D =[]
#     for item in dict_data:
#         a = [item ,dict_data[item]]
#         array_2D.append(a)
#     return array_2D
    
# normal_list = dict_to_2Darray(json.loads(items['normal']))
# print(normal_list)
# STARTUP_SIGNUP_TABLE = 'Store_Info'

# table = dynamodb.Table(STARTUP_SIGNUP_TABLE)
# key = 'TEST.jpg'
# key = key[:-4]
# print(key)
# num = 30
# table.update_item(
#         Key={
#             'store': key,
#         },
#         UpdateExpression="set person_now = :pn",
#         ExpressionAttributeValues={
#             ':pn': num,
#         },
#         ReturnValues="UPDATED_NEW"
#     )
    
# # res = table.scan()
# # print(res['Items'])
# store_info_list = res['Items']
# for store in store_info_list:
#     print(store)
# response = table.put_item(Item=item)
# response = table.delete_item(Key = {'store':'Bar'})

# res = table.get_item(Key={'store': 'KFC'})
# item = res['Item']
# print(item['contact'])
# print(type(item['contact']))
# print(json.loads(item['contact']))
# # print(type(json.loads(item['contact'])))
# print(item['tag'])
# print(type(item['tag']))
# print(item['tag'][0])
# dynamodb = boto3.resource(
#         'dynamodb', region_name=AWS_REGION)
# table = dynamodb.Table('Store_List')
# res = table.get_item(Key={'id': 'HotPot'})
# print(res['Item'])
# print(type(res['Item']))
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