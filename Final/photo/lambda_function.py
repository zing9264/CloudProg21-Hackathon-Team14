import requests
import json
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
    # TODO implement
    msg = json.loads(event["Records"][0]["body"])
    print("msg", msg)
    text = msg['text']
    # reply = msg['replyToken']
    if '照片' in text:
        # use userid to name the s3 jpg?
        userid = 'test2'
        print(object_url+userid+'jpg')
        photo_msg["originalContentUrl"] = object_url+userid+'.jpg'
        photo_msg["previewImageUrl"] = object_url+userid+'.jpg'
        data["messages"] = [photo_msg]
    elif '訂單狀態' in text:
        push_msg(msg['userid'])
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


def push_msg(userid):
    push = {
        "to": "Udd4ef86b0e0fda4235528d5f262c89d8",
        "messages": [
            {
                "type": "text",
                "text": "主動訊息測試"
            }
        ]
    }
    push['to'] = userid
    push_url = "https://api.line.me/v2/bot/message/push"
    response = requests.post(push_url, headers=headers, json=push)
    print(response)


"""
export AWS_DEFAULT_PROFILE=NTHU
cd photo
rm photo.zip
pip install -r requirements.txt -t ./
zip -r9 photo.zip ./
aws lambda update-function-code --function-name photo --zip-file fileb://photo.zip --region us-east-1
"""
