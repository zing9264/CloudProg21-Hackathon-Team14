import requests
import json
url = " https://api.line.me/v2/bot/message/reply"
auth_token = "Y9LesqC4GBjovyLxcZiljevh8i2t0ySIhHwTlRh13T6LNNI/3Jd3sT2PDADxgFex2o1gVrlbK1oT8gq9Oo0q8XdYMnmRE3bVkV48titam8dirGIRtwNwtqFRAUKlDKrsvnNCCVUDy7pBOCxHz8ptEwdB04t89/1O/w1cDnyilFU="
headers = {"Authorization": "Bearer " + auth_token}
data = {"replyToken": "", "messages": [{"type": "text", "text": "Hello, user"}]}


def lambda_handler(event, context):
    # TODO implement
    msg = json.loads(event["Records"][0]["body"])
    print("msg",msg)
    text = msg['text']
    reply = msg['replyToken']
    if '開鎖' in text:
        Unlock()
        data["messages"][0]["text"] = '已完成開鎖'
    elif '上鎖' in text:
        Locked()
        data["messages"][0]["text"] = '已完成上鎖'
    data["replyToken"] = msg["replyToken"]
    response = requests.post(url, headers=headers, json=data)
    print(response.text)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def Unlock():
    print("open")
    return


def Locked():
    print("open")
    return


"""
export AWS_DEFAULT_PROFILE=NTHU
cd box
rm box.zip
pip install -r requirements.txt -t ./
zip -r9 box.zip ./
aws lambda update-function-code --function-name box --zip-file fileb://box.zip --region us-east-1
"""