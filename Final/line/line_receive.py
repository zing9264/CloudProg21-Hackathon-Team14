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
    