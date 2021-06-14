import boto3

def get_all_Data_DBitem(tablename):
    dynamodb = boto3.resource(
        'dynamodb', region_name='us-east-1')
    table = dynamodb.Table(tablename)
    res = table.scan()
    data_info_list = res['Items']
    return data_info_list

if __name__ == '__main__':
    movie_resp = get_all_Data_DBitem('Final_deliveryDB')
    print(movie_resp)
