import boto3
# Get the service resource
sqs = boto3.resource('sqs')
# Create the queue. This returns an SQS.Queue instance
queue = sqs.get_queue_by_name(QueueName='test')
response = queue.send_message(MessageBody='world')

print(response.get('MessageId'))
print(response.get('MD5OfMessageBody'))

