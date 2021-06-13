import requests
import json
url = " https://api.line.me/v2/bot/message/reply"
auth_token = "Y9LesqC4GBjovyLxcZiljevh8i2t0ySIhHwTlRh13T6LNNI/3Jd3sT2PDADxgFex2o1gVrlbK1oT8gq9Oo0q8XdYMnmRE3bVkV48titam8dirGIRtwNwtqFRAUKlDKrsvnNCCVUDy7pBOCxHz8ptEwdB04t89/1O/w1cDnyilFU="
headers = {"Authorization": "Bearer " + auth_token}


a=requests.get('https://api.line.me/v2/bot/followers/ids',headers=headers)

print(a)
