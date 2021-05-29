import json
data = {"inputEmail": "A@AA", "inputPassword": "", "inputAddress": "XXX", "inputphone": "09", "inputstore": "QQQQ", "inputperson_max": "11", "normal-1": "A", "normal-price-1": "111", "normal-2": "B", "normal-price-2": "130", "discount-1": "AA", "discount-price-1": "222"}
item_list = ['inputEmail', 'inputPassword', 'inputAddress', 'inputphone', 'inputstore', 'inputperson_max', 'normal-1', 'normal-price-1', 'normal-2', 'normal-price-2', 'discount-1', 'discount-price-1']

normal_count = []
discount_count = []
for item in item_list:
    if 'normal' in item and 'price' not in item:
        normal_count.append(item)
    elif 'discount' in item and 'price' not in item:
        discount_count.append(item)
print(normal_count,discount_count)


user = {}
user['id'] = data['inputEmail']
user['password'] = data['inputPassword']

storeinfo = {'store': data['inputstore'], 'person_max': data['inputperson_max'],}
contact = {"phone":data['inputphone'], "address":data['inputAddress'] } 
normal = {}
discount = {}
for item in normal_count:
    normal[item] = data[item]
for item in discount_count:
    discount[item] = data[item]
print(normal)
print(json.dumps(normal))

initTableItem = {
    'store': 'HotPot',
    'person_max': 40,
    'person_now': 32,
    'contact': ' {"phone":"0800092000", "address":"XX區XX路XX號" } ',
    'normal': '{"A": 228, "B": 300 }',
    'discount': '{"A":200 } ',
    'tag': ['Chinese', 'HotPot']
}


def signup_data_parse(data,item_list):
    normal_count = []
    discount_count = []
    for item in item_list:
        if 'normal' in item and 'price' not in item:
            normal_count+=0.5
        elif 'discount' in item and 'price' not in item:
            discount_count+=0.5
    user = {}
    user['id'] = data['inputEmail']
    user['password'] = data['inputPassword']
    storeinfo = {}
    contact = {"phone":data['inputphone'], "address":data['inputAddress'] } 
    normal = {"A": 228, "B": 300 }
    
    return