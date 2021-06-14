# Copyright 2013. Amazon Web Services, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import json
from typing import ItemsView
import boto3
import requests
from datetime import datetime

import flask
from flask import request, Response, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Default config vals
THEME = 'default' if os.environ.get(
    'THEME') is None else os.environ.get('THEME')
FLASK_DEBUG = 'false' if os.environ.get(
    'FLASK_DEBUG') is None else os.environ.get('FLASK_DEBUG')

# Create the Flask app
application = flask.Flask(__name__)
# Load config values specified above
application.config.from_object(__name__)
# Load configuration vals from a file
# application.config.from_envvar('APP_CONFIG', silent=True)
application.config.from_pyfile('config.py')
application.secret_key = application.config['SECRET_KEY']
# Only enable Flask debugging if an env var is set to true
application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']

# DEFINE S3  source url
object_url = "https://"+application.config['S3'] + ".s3.amazonaws.com/"
# #這塊需要從資料庫撈資料 並用jinja2 渲染到前端


@application.route('/')
def preload():
    return flask.render_template('preload.html', flask_debug=application.debug)

@application.route('/index')
def welcome():
    theme = application.config['THEME']
    delivery_list = get_all_Data_DBitem(application.config['DELIVERY_LIST'])
    for i in range(len(delivery_list)):
        delivery_list[i]['name'] = get_DBitem(application.config['USER_LIST'], delivery_list[i]['id'])['name']
        delivery_list[i]['phone'] = get_DBitem(application.config['USER_LIST'], delivery_list[i]['id'])['phone']
    return flask.render_template('index.html', flask_debug=application.debug, deliverys=delivery_list, object_url=object_url)


@application.route('/<userId>/send_notify', methods=['GET'])
def send_notify(userId):
    creattime=request.args.get('creattime')
    table = boto3.resource('dynamodb', region_name=application.config['AWS_REGION']).Table(application.config['DELIVERY_LIST'])
    res = table.get_item(Key={'id': userId,'creattime':creattime})
    item = res['Item']
    print("----------send_notify------------")
    print(userId,creattime)
    response = table.update_item(
        Key={
            'id': userId,
            'creattime': creattime
        },
        UpdateExpression="set delivery_condition=:c",
        ExpressionAttributeValues={
            ':c': '交貨中'
        },
        ReturnValues="UPDATED_NEW"
    )
    print(response)
    push_msg(userId, item['productname'])
    print("----------send_end------------")
    

    return redirect(url_for('welcome'))

@application.route('/addDelivery')
def addDelivery():
    user_list = get_all_Data_DBitem(application.config['USER_LIST'])
    return flask.render_template('add_delivery.html', flask_debug=application.debug, users=user_list, usersforjs=json.dumps(user_list))

# 註冊帳號與所有資料


@application.route('/addDeliveryPost', methods=['POST'])
def addDeliveryPost():
    ddb_conn = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    delivery_data = dict()
    item_list = []
    for item in request.form:
        delivery_data[item] = request.form[item]
        item_list.append(item)
    print(item_list)
    print(delivery_data)
    delivery_data['creattime'] = datetime.now().strftime("%Y/%m/%d,%H:%M:%S")
    delivery_data['delivery_condition'] = '運送中'
    ddb_table = ddb_conn.Table(application.config['DELIVERY_LIST'])
    ddb_table.put_item(Item=delivery_data)
    #flash('SIGN UP SUCCESS')
    return redirect(url_for('preload'))


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 上傳圖片頁面
@application.route('/<userId>/upload_file_page')
def upload_file_page(userId):
    print(userId)
    return flask.render_template('upload_image.html', userId=userId, flask_debug=application.debug)

# 上傳圖片功能，會存檔到UPLOAD_FOLDER='static/uploads/' 之後要改成boto3 S3 bucket


@application.route('/<userId>/image_upload', methods=['POST'])
def storeimage_upload(userId):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return flask.render_template('upload_image.html', userId=userId, flask_debug=application.debug)
        file = request.files['file']
        if file == '':
            flash('No image selected for uploading')
            return flask.render_template('upload_image.html', userId=userId, flask_debug=application.debug)

        if file and allowed_file(file.filename):
            filename = userId+'.jpg'
            upload_to_S3(file, filename)
            print(filename)
            # file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            #print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed below')
            return flask.render_template('upload_image.html', filename=filename, storename=userId, object_url=object_url, flask_debug=application.debug)
        else:
            flash('Allowed image types are - png, jpg, jpeg')
            return flask.render_template('upload_image.html', storename=userId, flask_debug=application.debug)

# 回傳圖片位置 UPLOAD_FOLDER='static/uploads/' 之後要改成boto3 S3 bucket


@application.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

# push msg to line (without replytoken)
def push_msg(userid,product):
    auth_token = "Y9LesqC4GBjovyLxcZiljevh8i2t0ySIhHwTlRh13T6LNNI/3Jd3sT2PDADxgFex2o1gVrlbK1oT8gq9Oo0q8XdYMnmRE3bVkV48titam8dirGIRtwNwtqFRAUKlDKrsvnNCCVUDy7pBOCxHz8ptEwdB04t89/1O/w1cDnyilFU="
    headers = {"Authorization": "Bearer " + auth_token}
    push = {
        "to": " ",
        "messages": [
            {
                "type": "text",
                "text": "你的貨物「"+product+"」已送達"
            },
            {
                "type": "text",
                "text": "請確認並開鎖"
            }
        ]
    }
    push['to'] = userid
    push_url = "https://api.line.me/v2/bot/message/push"
    response = requests.post(push_url, headers=headers, json=push)
    print(response)

def get_all_Data_DBitem(tablename):
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(tablename)
    res = table.scan()
    data_info_list = res['Items']
    return data_info_list


def dict_to_2Darray(dict_data):
    array_2D = []
    for item in dict_data:
        a = [item, dict_data[item]]
        array_2D.append(a)
    return array_2D


def add_DBitem(tablename, item):
    # it's easy to update or add (update item just use same key)
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(tablename)
    response = table.put_item(Item=item)
    print(response)
    return


def delete_DBitem(tablename, userid):
    # storename must be string , use key "store" to delete item
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(tablename)
    response = table.delete_item(Key={'id': userid})
    print(response)
    return


def get_DBitem(tablename, userid):
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(tablename)
    res = table.get_item(Key={'id': userid})
    item = res['Item']
    # json.loads(item['contact']) --> to load json
    # item['tag'][0] --> to get tag
    return item

# parse example


def parse_db_item(storename):
    item = get_DBitem(application.config['STORE_INFO'], storename)
    person_now = item['person_now']         # int?
    person_max = item['person_max']         # int?
    contact = json.loads(item['contact'])   # dict
    normal = json.loads(item['normal'])     # dict
    discount = json.loads(item['discount'])  # dict
    tag = item['tag']  # list


def upload_to_S3(image, name):
    s3 = boto3.client('s3')
    s3.upload_fileobj(image, application.config['S3'], name, ExtraArgs={
                      'ACL': 'public-read', 'ContentType': 'image/jpeg'})
    return


# Connect to DynamoDB and get ref to Table
initUserList = {
    'id': 'TestUser001',
    'name': '陳先生',
    'Box': ['A_box'],
    'address': ['300新竹市東區光復路二段101號'],
    'phone': '0989744940'
}

initDeliveryList = {
    'id': 'TestUser001',
    'creattime': datetime(2015, 1, 1).strftime("%Y/%m/%d,%H:%M:%S"),
    'address': '300新竹市東區光復路二段101號',
    'delivery_condition': '運送中',  # 運送中、交貨中、已送達
    'productname': '小熊玩偶',
}

# check resource exist


def check_or_create():
    # Get the service resource
    ddb_conn = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    sqs = boto3.resource('sqs', region_name=application.config['AWS_REGION'])
    s3 = boto3.client('s3')
    isbucketExist = False
    # create S3
    response = s3.list_buckets()

    for bucket in response['Buckets']:
        if bucket["Name"] == application.config['S3']:
            isbucketExist = True

    if isbucketExist == False:
        try:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=application.config['S3'])
        except Exception as e:
            print(e)

    # create table
    try:
        # create DELIVERY info table
        ddb_conn.create_table(
            TableName=application.config['DELIVERY_LIST'],
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'},{'AttributeName': 'creattime', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},{'AttributeName': 'creattime', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})
        # create user list table
        ddb_conn.create_table(
            TableName=application.config['USER_LIST'],
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})

    except Exception as e:
        print(e)
        ddb_table = ddb_conn.Table(application.config['DELIVERY_LIST'])
        ddb_table = ddb_conn.Table(application.config['USER_LIST'])
        print("table exists")

    try:
        ddb_table = ddb_conn.Table(application.config['DELIVERY_LIST'])
        ddb_table.put_item(Item=initDeliveryList)
        ddb_table = ddb_conn.Table(application.config['USER_LIST'])
        ddb_table.put_item(Item=initUserList)
        print("init DB table")
    except:
        print("init DB item fail")

#check_or_create()


if __name__ == '__main__':
    # application.run(debug=True,host='127.0.0.1')
    application.run(host='0.0.0.0')
