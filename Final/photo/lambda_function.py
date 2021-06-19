import requests
import json
import boto3

url = " https://api.line.me/v2/bot/message/reply"
auth_token = "Y9LesqC4GBjovyLxcZiljevh8i2t0ySIhHwTlRh13T6LNNI/3Jd3sT2PDADxgFex2o1gVrlbK1oT8gq9Oo0q8XdYMnmRE3bVkV48titam8dirGIRtwNwtqFRAUKlDKrsvnNCCVUDy7pBOCxHz8ptEwdB04t89/1O/w1cDnyilFU="
headers = {"Authorization": "Bearer " + auth_token}
data = {"replyToken": "", "messages": [
    {"type": "text", "text": "Hello, user"}]}
photo_msg = {"type": "image", "originalContentUrl": "圖片網址",
             "previewImageUrl": "縮圖網址"}
text_msg = {"type": "text", "text": "Hello, user"}
S3 = 'nthu-final-team14'
# DEFINE S3  source url
object_url = "https://nthu-final-team14.s3.amazonaws.com/"

def lambda_handler(event, context):
    print(event)
    # TODO implement
    msg = json.loads(event["Records"][0]["body"])
    print("msg", msg)
    text = msg['text']
    userid=msg['userid']
    # reply = msg['replyToken']
    if '照片' in text:
        # use userid to name the s3 jpg?
        print(object_url+userid+'.jpg')
        photo_msg["originalContentUrl"] = object_url+userid+'.jpg'
        photo_msg["previewImageUrl"] = object_url+userid+'.jpg'
        data["messages"] = [photo_msg]
    elif '訂單狀態' in text:
        print(userid)
        delivery_list = get_DBitem('Final_deliveryDB',userid)
        order_info = []
        for i in range(len(delivery_list)):
            if delivery_list[i]['id'] == userid:
                order_info.append("您的商品「"+delivery_list[i]['productname']+"」\n目前狀態："+delivery_list[i]['delivery_condition'])
        push_msg(msg['userid'],order_info)
        return {
            'statusCode': 200,
            'body': json.dumps('push msg')
        }
    elif '說明' in text:
        push_msg(msg['userid'],['歡迎使用智慧包裹箱服務，你可以透過簡單的line回覆來控制你的包裹箱\n下方按鈕可控制開關鎖，也可以查詢訂單，輸入「照片」及會回傳目前最新包裹箱照片。'])
        return {
            'statusCode': 200,
            'body': json.dumps('push msg')
        }
    else:
        text_msg['text'] = text
        data["messages"] = [text_msg]

    print(data)
    data["replyToken"] = msg["replyToken"]
    response = requests.post(url, headers=headers, json=data)
    print(response.text)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

# push msg to line (without replytoken)
def push_msg(userid,order_info):
    push = {
        "to": "Udd4ef86b0e0fda4235528d5f262c89d8",
        "messages": []
    }
    push['to'] = userid
    infolist = []
    for info in order_info:
        text_msg = {"type": "text", "text": info}
        infolist.append(text_msg)
    push['messages'] = infolist
    push_url = "https://api.line.me/v2/bot/message/push"
    response = requests.post(push_url, headers=headers, json=push)
    print(response)

def get_DBitem(tablename, userid):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(tablename)
    res = table.scan()
    data_info_list = res['Items']
    # print(data_info_list)
    # json.loads(item['contact']) --> to load json
    # item['tag'][0] --> to get tag
    return data_info_list

"""
export AWS_DEFAULT_PROFILE=NTHU
cd photo
rm photo.zip
pip install -r requirements.txt -t ./
zip -r9 photo.zip ./
aws lambda update-function-code --function-name photo --zip-file fileb://photo.zip --region us-east-1
"""