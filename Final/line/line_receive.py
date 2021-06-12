import json
import boto3

region = "us-east-1"
def lambda_handler(event, context):
    toQ = {}
    parse_line_event = get_text(event)
    print("line event parse", parse_line_event)
    print("reply:", parse_line_event["replyToken"])
    print("msg text:", parse_line_event["message"]["text"])
    print("userid", parse_line_event["source"]["userId"])
    toQ['replyToken'] = parse_line_event["replyToken"]
    toQ['userid'] = parse_line_event["source"]["userId"]
    toQ['text'] = parse_line_event["message"]["text"]
    
    sqs = boto3.resource('sqs',region_name=region)
    if "開鎖" in parse_line_event["message"]["text"] or "上鎖" in parse_line_event["message"]["text"]:
        queue = sqs.get_queue_by_name(QueueName='box')
    else: 
        queue = sqs.get_queue_by_name(QueueName='photo')
    
    res = queue.send_message(MessageBody=json.dumps(toQ))
    # print(res)
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
def get_text(event):
    # print("event", event)
    body = event["body"]
    # print("body:", body)
    # print(type(body))
    body = json.loads(body)
    events = body["events"][0]
    return events
    
def line_handler(event, queuename):
    # linemsg = {"line":{"reply":{"source":{}}}}
    # e = event.copy()
    toQ = {}
    try:
        path = event["path"][1:]
        toQ[path] = {"reply": {}}  # line
        parse_line_event = get_text(event)
        print("line event parse", parse_line_event)
        print("reply:", parse_line_event["replyToken"])
        print("msg text:", parse_line_event["message"]["text"])
        print("userid", parse_line_event["source"]["userId"])
        toQ["url"] = parse_line_event["message"]["text"]
        if check_url(toQ["url"]):
            print(f"{toQ['url']} is a valid url")
            parse_line_event.pop("message")
            toQ[path]["reply"] = parse_line_event
            # linemsg["userId"] = parse_line_event["source"]["userId"]
            # linemsg["replyToken"] = parse_line_event["replyToken"]œ
            # toQ[path]["reply"]["replyToken"] = parse_line_event["replyToken"]
            # toQ[path]["reply"]["type"] = parse_line_event["type"]
            # toQ[path]["reply"]["mode"] = parse_line_event["type"] 
            # linemsg["text"] = parse_line_event["message"]["text"]
        else:
            print(f"{parse_line_event['message']['text']} is not a valid url")
    except:
        print("get line parse fail")

    # try:
    # Get the service resource
    sqs = boto3.resource("sqs", region_name=region)
    try:
        queue = sqs.get_queue_by_name(QueueName=queuename)
        res = queue.send_message(MessageBody=json.dumps(toQ))
        print("check:", json.dumps(toQ))
        print("res", res)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "hi,queue:" + str(queuename) + ".\n",
        }
    except:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": "this queue doesn't exist \n",
        }