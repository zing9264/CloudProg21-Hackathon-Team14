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

import flask
from flask import request, Response


import boto3

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

# Connect to DynamoDB and get ref to Table

# check resource exist


def check_or_create():
    # Get the service resource
    ddb_conn = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    sqs = boto3.resource('sqs', region_name=application.config['AWS_REGION'])
    try:
        ddb_conn.create_table(
            TableName=application.config['STARTUP_SIGNUP_TABLE'],
            KeySchema=[{'AttributeName': 'name', 'KeyType': 'HASH'},
                       {'AttributeName': 'email', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[{'AttributeName': 'name', 'AttributeType': 'S'},
                                  {'AttributeName': 'email', 'AttributeType': 'S'}],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
    # ddb_table = ddb_conn.Table(STARTUP_SIGNUP_TABLE)
    except:
        ddb_table = ddb_conn.Table(application.config['STARTUP_SIGNUP_TABLE'])
        print("table exists")
    try:
        print("check sqs...")
        queue = sqs.get_queue_by_name(QueueName=application.config['SQS'])
    except:
        print("sqs doesn't exist , create table ...")
        sqs.create_queue(QueueName=application.config['SQS'])


@application.route('/')
def welcome():
    theme = application.config['THEME']
    return flask.render_template('index.html', theme=theme, flask_debug=application.debug)


@application.route('/signup', methods=['POST'])
def signup():
    signup_data = dict()
    for item in request.form:
        signup_data[item] = request.form[item]
    try:
        send_sqs(signup_data)
        putDB_signup(signup_data)
    except ConditionalCheckFailedException:
        return Response("", status=409, mimetype='application/json')

    return Response(json.dumps(signup_data), status=201, mimetype='application/json')


'''
def store_in_dynamo(signup_data):
    signup_item = Item(ddb_table, data=signup_data)
    signup_item.save()
'''


def send_sqs(signup_data):
    sqs = boto3.resource('sqs', region_name=application.config['AWS_REGION'])
    queue = sqs.get_queue_by_name(QueueName=application.config['SQS'])
    response = queue.send_message(MessageBody=json.dumps(signup_data))
    print(signup_data)
    print(response.get('MessageId'))
    print(response.get('MD5OfMessageBody'))
    return response


def putDB_signup(signup_data):
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(application.config['STARTUP_SIGNUP_TABLE'])
    response = table.put_item(Item=signup_data)
    print(response)
    return


check_or_create()

if __name__ == '__main__':
    # application.run(debug=True,host='127.0.0.1')
    application.run(host='0.0.0.0')
