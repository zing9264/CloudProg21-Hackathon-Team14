import boto3
# Receive the message from SQS Tutorial:https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html

# Create SQS client
sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/662802416147/N'

# Receive message from SQS queue
response = sqs.receive_message(QueueUrl=queue_url)
msg = response['Messages'][0]
print(msg['Body'])
