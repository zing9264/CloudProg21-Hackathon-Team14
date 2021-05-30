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
from flask import request, Response, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
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

# ============================== login =================================
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.session_protection = "strong"
login_manager.login_view = 'loginpage'
class User(UserMixin):
    pass

def check_user(id):
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(application.config['USER_LIST'])
    try:
        res = table.get_item(Key={'id': id})
        return res['Item']
    except:
        print("User doesn't exist")
        return None
        
@login_manager.user_loader
def load_user(id):
    if check_user(id) is not None:
        curr_user = User()
        curr_user.id = id
    return curr_user
    
@application.route('/sign_up')
def sign_uppage():
    return flask.render_template('sign_up_restaurant.html', flask_debug=application.debug)

@application.route('/login', methods=['GET','POST'])
def loginpage():
    id = request.form.get('inputEmail')
    password = request.form.get('inputPassword')
    remember = True if request.form.get('remember') else False
    # print(id)
    user = check_user(id)
    if user is not None and password == user['password']:
        curr_user = User()
        curr_user.id = id
        print(curr_user)
        login_user(curr_user,remember=remember)
        next = request.args.get('next')
        print(request.args)
        if not next_is_valid(next):
            #  如果使用者沒有該url權限，那就reject掉。
            return 'Bad Boy!!'
        return redirect(next or url_for('welcome'))
    # elif user is not None :
    #     flash('Wrong username or password!')
        
    return flask.render_template('login.html', flask_debug=application.debug)
def next_is_valid(url):
    return True
# define logout
@application.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You already logout !!!')
    return redirect(url_for('welcome'))
# ============================== login =================================

# DEFINE S3  source url
object_url = "https://"+application.config['S3'] +".s3.amazonaws.com/"
# #這塊需要從資料庫撈資料 並用jinja2 渲染到前端
@application.route('/')
def welcome():
    theme = application.config['THEME']
    store_list = get_all_store_DBitem(application.config['STORE_INFO'])
    return flask.render_template('index.html', theme=theme, flask_debug=application.debug , stores = store_list, object_url=object_url)


#店家詳細資料這塊需要傳入所有資料庫變數，用jinja2 render出來
@application.route('/storepage/<storename>')
def storepage(storename):
    print(storename)
    storeinfo =get_DBitem(application.config['STORE_INFO'],storename)
    contact = json.loads(storeinfo['contact'])   # dict
    # turn dict to 2D array in order to use jinja to show the info in DB
    normal = dict_to_2Darray(json.loads(storeinfo['normal']))     
    discount = dict_to_2Darray(json.loads(storeinfo['discount']))  
    return flask.render_template('storepage.html',
                                flask_debug=application.debug,
                                info = storeinfo,
                                contact = contact,
                                normal = normal,
                                object_url=object_url,
                                discount = discount)

 
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#上傳圖片頁面
@application.route('/storepage/<storename>/upload_file_page')
@login_required
def upload_file_page(storename):
    print(storename)
    return flask.render_template('upload_image.html', storename=storename, flask_debug=application.debug)

#上傳圖片功能，會存檔到UPLOAD_FOLDER='static/uploads/' 之後要改成boto3 S3 bucket
@application.route('/storepage/<storename>/image_upload', methods=['POST'])
@login_required
def storeimage_upload(storename):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return flask.render_template('upload_image.html', storename=storename, flask_debug=application.debug)
        file = request.files['file']
        if file == '':
            flash('No image selected for uploading')
            return flask.render_template('upload_image.html', storename=storename, flask_debug=application.debug)

        if file and allowed_file(file.filename):
            filename = storename+'.jpg'
            upload_to_S3(file,filename)
            # file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            #print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed below')
            return flask.render_template('upload_image.html', filename=filename ,storename=storename, flask_debug=application.debug)
        else:
            flash('Allowed image types are - png, jpg, jpeg')
            return flask.render_template('upload_image.html', storename=storename, flask_debug=application.debug)

#回傳圖片位置 UPLOAD_FOLDER='static/uploads/' 之後要改成boto3 S3 bucket
@application.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

#更新店家資料頁面 這塊需要傳入所有資料庫變數，用jinja2 render出來
@application.route('/storepage/<storename>/update_storepage')
@login_required
def storeupdate_storepage(storename):
    userinfo = check_user(current_user.id)
    print(userinfo)
    storeinfo =get_DBitem(application.config['STORE_INFO'],storename)
    contact = json.loads(storeinfo['contact'])   # dict
    # turn dict to 2D array in order to use jinja to show the info in DB
    normal = dict_to_2Darray(json.loads(storeinfo['normal']))     
    discount = dict_to_2Darray(json.loads(storeinfo['discount']))
    if userinfo['storename'] == storename:
        return flask.render_template('update_storepage.html', info = storeinfo,
                                contact = contact,
                                normal = normal,
                                discount = discount, flask_debug=application.debug)
    else:
        flash('This is not your store !!!')
        return redirect(url_for('storepage',storename=storename))
    # return flask.render_template('update_storepage.html', storename=storename, flask_debug=application.debug)

#更新店家資料功能 這塊需要驗證登入  這部分前端動態處理還沒完成
@application.route('/storepage/<storename>/updateFormPost')
@login_required
def update_DBdata(storename):
    update_data = dict()
    item_list = []
    data = {}
    for item in request.form:
        data[item] = request.form[item]
        item_list.append(item)
    print(data)
    print(item_list)
    return flask.render_template('storepage.html', storename=storename, flask_debug=application.debug)

#註冊帳號與所有資料
@application.route('/signupFormPost', methods=['POST'])
def signupFormPost():
    signup_data = dict()
    item_list = []
    for item in request.form:
        signup_data[item] = request.form[item]
        item_list.append(item)
    signup_data_parse(signup_data, item_list)
    flash('SIGN UP SUCCESS')
    return redirect(url_for('welcome'))

#註冊帳號用的語法分析器
def signup_data_parse(data, item_list):
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    normal_count = []
    discount_count = []
    for item in item_list:
        if 'normal' in item and 'price' not in item:
            normal_count.append(item)
        elif 'discount' in item and 'price' not in item:
            discount_count.append(item)
    # user table
    user = {}
    user['id'] = data['inputEmail']
    user['password'] = data['inputPassword']
    user['storename'] = data['inputstore']
    table = dynamodb.Table(application.config['USER_LIST'])
    response = table.put_item(Item=user)
    print("user info", response)
    # store info table
    storeinfo = {'store': data['inputstore'],
                 'person_max': data['inputperson_max'], 'tag': data['tag'].split()}
    contact = {'phone': data['inputphone'], 'address': data['inputAddress']}
    normal = {}
    discount = {}
    for i, item in enumerate(normal_count):
        pricename = 'normal-price-'+str(i+1)
        normal[data[item]] = data[pricename]
    for i, item in enumerate(discount_count):
        pricename = 'discount-price-'+str(i+1)
        discount[data[item]] = data[pricename]
    tag = data['tag'].split()
    storeinfo['contact'] = json.dumps(contact)
    storeinfo['normal'] = json.dumps(normal)
    storeinfo['discount'] = json.dumps(discount)

    table = dynamodb.Table(application.config['STORE_INFO'])
    response = table.put_item(Item=storeinfo)
    print("store info", response)

    return

@application.route('/test')
def test():
    store_list = get_all_store_DBitem(application.config['STORE_INFO'])
    storename = '87店'
    storeinfo =get_DBitem(application.config['STORE_INFO'],storename)
    contact = json.loads(storeinfo['contact'])   # dict
    normal = dict_to_2Darray(json.loads(storeinfo['normal']))     
    discount = dict_to_2Darray(json.loads(storeinfo['discount']))  
    return flask.render_template('test.html', 
            flask_debug=application.debug,
            info = storeinfo,
            contact = contact,
            normal = normal,
            discount = discount)
    
def get_all_store_DBitem(tablename):
    dynamodb = boto3.resource('dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(tablename)
    res = table.scan()
    store_info_list = res['Items']
    return store_info_list

def dict_to_2Darray(dict_data):
    array_2D =[]
    for item in dict_data:
        a = [item ,dict_data[item]]
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

def delete_DBitem(tablename, storename):
    # storename must be string , use key "store" to delete item
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(tablename)
    response = table.delete_item(Key={'store': storename})
    print(response)
    return


def get_DBitem(tablename, storename):
    dynamodb = boto3.resource(
        'dynamodb', region_name=application.config['AWS_REGION'])
    table = dynamodb.Table(tablename)
    res = table.get_item(Key={'store': storename})
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


def upload_to_S3(image,name):
    s3 = boto3.client('s3')
    s3.upload_fileobj(image,application.config['S3'],name,ExtraArgs={'ACL':'public-read', 'ContentType': 'image/jpeg'})
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
    'password': '1111111',
    'storename':'HotPot'
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
        # create store info table
        ddb_conn.create_table(
            TableName=application.config['STORE_INFO'],
            KeySchema=[{'AttributeName': 'store', 'KeyType': 'HASH'}],
            AttributeDefinitions=[
                {'AttributeName': 'store', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})
        # create user list table
        ddb_conn.create_table(
            TableName=application.config['USER_LIST'],
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})
    except:
        ddb_table = ddb_conn.Table(application.config['STORE_INFO'])
        ddb_table = ddb_conn.Table(application.config['USER_LIST'])
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
        ddb_table = ddb_conn.Table(application.config['USER_LIST'])
        ddb_table.put_item(Item=initUserList)
        print("init DB table")
    except:
        print("init DB item fail")

# check_or_create()


if __name__ == '__main__':
    # application.run(debug=True,host='127.0.0.1')
    application.run(host='0.0.0.0')
