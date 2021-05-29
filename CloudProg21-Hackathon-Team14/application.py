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
import boto3

import flask
from flask import request, Response ,redirect, url_for ,flash
from flask_login import LoginManager,UserMixin,login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

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

# Only enable Flask debugging if an env var is set to true
application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']

## LOGIN
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
class User(UserMixin):
    pass
@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

@application.route('/')
def welcome():
    theme = application.config['THEME']
    return flask.render_template('index.html', theme=theme, flask_debug=application.debug)

@application.route('/login')
def loginpage():
    return flask.render_template('login.html', flask_debug=application.debug)


@application.route('/signup', methods=['POST'])
def signup():
    signup_data = dict()
    for item in request.form:
        signup_data[item] = request.form[item]
    try:
        add_DBitem(application.config['STORE_LIST'],signup_data)
    except ConditionalCheckFailedException:
        return Response("", status=409, mimetype='application/json')

    return Response(json.dumps(signup_data), status=201, mimetype='application/json')

@application.route('/login',methods=['POST'])
def login_post():
    email = request.form.get('id')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    
    user = {}
    user['id'] = email
    user['password'] = password
    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) # if the user doesn't exist or password is wrong, reload the page
    print(user)
    login_user(user, remember=remember)
    return redirect(url_for('profile'))
    
def send_sqs(signup_data):
    sqs = boto3.resource('sqs', region_name=application.config['AWS_REGION'])
    queue = sqs.get_queue_by_name(QueueName=application.config['SQS'])
    response = queue.send_message(MessageBody=json.dumps(signup_data))
    print(signup_data)
    print(response.get('MessageId'))
    print(response.get('MD5OfMessageBody'))
    return response


def add_DBitem(tablename,item):
    # it's easy to update or add (update item just use same key)
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(tablename)
    response = table.put_item(Item=item)
    print(response)
    return


def delete_DBitem(tablename,store_name):
    # store_name must be string , use key "store" to delete item
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(tablename)
    response = table.delete_item(Key={'store': store_name})
    print(response)
    return


def get_DBitem(tablename,store_name):
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(tablename)
    res = table.get_item(Key={'store': store_name})
    item = res['Item']
    # json.loads(item['contact']) --> to load json
    # item['tag'][0] --> to get tag
    return item

# parse example
def parse_db_item(store_name):
    item = get_DBitem(application.config['STORE_INFO'],store_name)
    person_now = item['person_now']         # int?
    person_max = item['person_max']         # int?
    contact = json.loads(item['contact'])   # dict
    normal = json.loads(item['normal'])     # dict
    discount = json.loads(item['discount'])  # dict
    tag = item['tag']  # list

def check_user(store_id):
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(application.config['STORE_LIST'])
    try:
        res = table.get_item(Key={'id': store_id})
        return res['password']
    except:
        print("password not match")
        return None

def upload_to_S3(image):
    s3 = boto3.client('s3')
    s3.upload_file(image)
    return

# Connect to DynamoDB and get ref to Table
initTableItem = {
    'store': 'HotPot',
    'person_max': 40,
    'person_now': 32,
    'contact': ' {"phone":"0800092000", "address":"XX區XX路XX號" } ',
    'normal': '{"A": 228, "B": 300 }',
    'discount': '{"A":200 } ',
    'tag': ['Chinese', 'HotPot']
}
initUserList = {
    'id': 'HotPot@mail.com',
    'password': '1111111'
}
# check resource exist
def check_or_create():
    # Get the service resource
    ddb_conn = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    sqs = boto3.resource('sqs', region_name=application.config['AWS_REGION'])
    s3 = boto3.client('s3')
    isbucketExist=False
    # create S3
    response = s3.list_buckets()
    
    for bucket in response['Buckets']:
            if bucket["Name"] == application.config['S3']:
                isbucketExist=True
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket=application.config['S3'])
    
    # create table
    try:
        # create store info table
        ddb_conn.create_table(
            TableName=application.config['STORE_INFO'],
            KeySchema=[{'AttributeName': 'store', 'KeyType': 'HASH'}],
            AttributeDefinitions=[
                {'AttributeName': 'store', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})
        # create user list table
        ddb_conn.create_table(
            TableName=application.config['STORE_LIST'],
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})
    except:
        ddb_table = ddb_conn.Table(application.config['STORE_INFO'])
        ddb_table = ddb_conn.Table(application.config['STORE_LIST'])
        print("table exists")

    try:
        print("check sqs...")
        queue = sqs.get_queue_by_name(QueueName=application.config['SQS'])
    except:
        print("sqs doesn't exist , create sqs ...")
        sqs.create_queue(QueueName=application.config['SQS'])

    try:
        ddb_table = ddb_conn.Table(application.config['STORE_INFO'])
        ddb_table.put_item(Item=initTableItem)
        ddb_table = ddb_conn.Table(application.config['STORE_LIST'])
        ddb_table.put_item(Item=initUserList)
        print("init DB table")
    except:
        print("init DB item fail")


check_or_create()

if __name__ == '__main__':
    # application.run(debug=True,host='127.0.0.1')
    application.run(host='0.0.0.0')
