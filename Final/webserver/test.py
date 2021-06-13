import json
import boto3

data = {'inputEmail': 'AAA@AA', 'inputPassword': 'A', 'inputAddress': 'XXX', 'inputphone': '0909', 'inputstore': 'AAA', 'inputperson_max': '20', 'normal-1': 'AA', 'normal-price-1': '12', 'normal-2': 'BB', 'normal-price-2': '1212', 'discount-1': 'AAA', 'discount-price-1': '121212', 'tag': 'KK QQ'}
item_list = ['inputEmail', 'inputPassword', 'inputAddress', 'inputphone', 'inputstore', 'inputperson_max', 'normal-1', 
            'normal-price-1', 'normal-2', 'normal-price-2', 'discount-1', 'discount-price-1']

normal_count = []
discount_count = []
for item in item_list:
    if 'normal' in item and 'price' not in item:
        normal_count.append(item)
    elif 'discount' in item and 'price' not in item:
        discount_count.append(item)
print(normal_count,discount_count)

user = {}
user['id'] = data['inputEmail']
user['password'] = data['inputPassword']

storeinfo = {'store': data['inputstore'], 'person_max': data['inputperson_max'],'tag':data['tag'].split()}
contact = {'phone':data['inputphone'], 'address':data['inputAddress'] } 
normal = {}
discount = {}
for i,item in enumerate(normal_count):
    pricename = 'normal-price-'+str(i+1)
    normal[data[item]] = data[pricename]
for i,item in enumerate(discount_count):
    pricename = 'discount-price-'+str(i+1)
    discount[item] = data[pricename]
tag = data['tag'].split()
print(normal)
print(json.dumps(normal))
storeinfo['contact'] = json.dumps(contact)
storeinfo['normal'] = json.dumps(normal)
storeinfo['discount'] = json.dumps(discount)
print(storeinfo)


STARTUP_SIGNUP_TABLE = 'Store_Info'
AWS_REGION = 'us-east-1'
dynamodb = boto3.resource(
    'dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(STARTUP_SIGNUP_TABLE)
response = table.put_item(Item=storeinfo)

# def signup_data_parse(data,item_list):
#     normal_count = []
#     discount_count = []
#     for item in item_list:
#         if 'normal' in item and 'price' not in item:
#             normal_count+=0.5
#         elif 'discount' in item and 'price' not in item:
#             discount_count+=0.5
#     user = {}
#     user['id'] = data['inputEmail']
#     user['password'] = data['inputPassword']
#     storeinfo = {}
#     contact = {"phone":data['inputphone'], "address":data['inputAddress'] } 
#     normal = {"A": 228, "B": 300 }
    
#     return